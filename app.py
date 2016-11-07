from bottle import get, post, run, static_file, request
import random


annotations = {}


@get('/<path:re:css|js|img|boucles_de_garches>/<fname>')
@get('/index.html')
@get('/')
def serve_css(fname="index.html", path="."):
    return static_file(fname, root=path)


@get("/random")
def get_random_pic():
    imgs = [
        "boucles_de_garches/14706744_1136003306491793_6299872446280854598_o.jpg",
        "boucles_de_garches/14714885_1136008809824576_3201558256798966930_o.jpg",
        "boucles_de_garches/14715461_1136009669824490_7181235540856504290_o.jpg",
    ]

    img = random.choice(imgs)
    img = {
        "img": img,
        "annotations": annotations.get(img),
    }
    return img


@post("/save")
def save_and_get_random_pic():
    save = request.json
    annotations[save["img"]] = save["annotations"]
    return get_random_pic()


run(host='localhost', port=8080)
