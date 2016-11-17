from bottle import run, get, post, static_file, request
import random
from pathlib import Path
import pymysql
import sys
import json


config = json.load(open("config.json"))


# Scan all pictures to annotate
all_photos = [str(p)[3:] for p in Path("../photos/").glob("**/*.jpg")]

print("All photos loaded")
sys.stdout.flush()


def connect():
    sql = config["sql"]
    host, user, passwd = sql["host"], sql["user"], sql["passwd"], sql["db"]
    return pymysql.connect(host=host, user=user, passwd=passwd, db=db, autocommit=False)


@get('/<path:re:css|js|img|(photos/.*)>/<fname>')
@get('/index.html')
@get('/')
def serve_css(fname="index.html", path="."):
    print(path)
    if path.startswith("photos/"):
        path = "../" + path
    return static_file(fname, root=path)


@get("/random")
def get_random_pic():
    img = random.choice(all_photos)
    return get_pic(img)


def annotation_from_row(img, row):
    text, x, y, width, height = row
    annotation = {
	    "img": img,
	    "text": text,
	    "box": {
		    "x": x,
		    "y": y,
		    "width": width,
		    "height": height,
    }}
    return annotation


@get("/get/<img:path>")
def get_pic(img):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            (SELECT bib, x, y, width, height FROM bibs WHERE img = %s)
            UNION
            (SELECT brand, x, y, width, height FROM brands WHERE img = %s)
            """, (img, img))
        annotations = [annotation_from_row(img, row) for row in cur.fetchall()]
    
        cur.execute("SELECT img FROM annotated ORDER BY datetime DESC LIMIT 5")
        last_imgs = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT brand, count(*) FROM brands GROUP BY brand ORDER BY count(*) DESC LIMIT 5")
        best_brands = [(r[0], r[1]) for r in cur.fetchall()]

    img = {
        "img": img,
        "annotations": annotations,
        "last_imgs": last_imgs,
	"best_brands": best_brands,
    }
    return img


@post("/save")
def save_and_get_random_pic():
    save = request.json
    img = save["img"]
    bibs = []
    brands = []

    for annotation in save["annotations"]:
        text = annotation["text"]
        text = text.lower().strip()
        box = annotation["box"]
        record = (img, text, box["x"], box["y"], box["width"], box["height"])
        if text != "2xu" and text[0].isdigit():
            bibs.append(record)
        else:
            brands.append(record)

    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE annotated, bibs, brands 
            FROM annotated
            LEFT JOIN bibs USING(img)
            LEFT JOIN brands USING(img)
            WHERE img = %s
            """, (img, ))

        cur.execute("INSERT INTO annotated (img) VALUES (%s)", (img, ))

        if len(bibs) > 0:
            print(repr(bibs))
            cur.executemany("INSERT INTO bibs (img, bib, x, y, width, height) VALUES (%s, %s, %s, %s, %s, %s)", bibs)
        if len(brands) > 0:
            cur.executemany("INSERT INTO brands (img, brand, x, y, width, height) VALUES (%s, %s, %s, %s, %s, %s)", brands)
    conn.commit()

    return get_random_pic()


run(host='localhost', port=8080, server="cherrypy")
