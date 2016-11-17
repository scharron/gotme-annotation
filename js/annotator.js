angular.module('app', [])
.controller('AnnotatorController', function($http) {
    var ctrl = this;

    ctrl.img = "/img/gotme.png";
    ctrl.element = document.getElementById('img')
    ctrl.annotations = [];
    ctrl.last = [];
    ctrl.brands = [];

    ctrl.element.onload = function() {
        anno.reset(ctrl.element)
        anno.makeAnnotatable(ctrl.element); 
        angular.forEach(ctrl.annotations, function(annot) {
            annot.src = ctrl.element.src;
            console.log(annot);
            anno.addAnnotation(annot);
        });
    }

    function processResponse(response) {
	var my_annotations = [];
        angular.forEach(response.data.annotations, function(annot) {
            var my_annotation = {
                src : response.data.img,
                text : annot.text,
                shapes : [{
                    type : 'rect',
                    units: 'pixel',
                    geometry : { 
                        x : annot.box.x,
                        y : annot.box.y,
                        width : annot.box.width,
                        height : annot.box.height,
                    }
                }]
            };
            console.log(my_annotation);
            my_annotations.push(my_annotation);
        });
        ctrl.annotations = my_annotations;
        ctrl.img = response.data.img;
        ctrl.brands = response.data.best_brands;
        ctrl.last = response.data.last_imgs;
    }

    ctrl.loadNext = function() {
        $http.get("/random").then(function (response) {
	    processResponse(response);
        }, function (error) {
            console.log(error);
            //
        })
    }

    ctrl.loadImg = function(img) {
        $http.get("/get/" + img).then(function (response) {
	    processResponse(response);
        }, function (error) {
            console.log(error);
            //
        })
    }

    ctrl.saveAndLoadNext = function() {
        var data = anno.getAnnotations();
        var my_annotations = [];
        angular.forEach(data, function(annot) {
            console.log(annot);
            var my_annotation = { "text": annot.text };
            var box = annot.shapes[0].geometry;
            if (annot.shapes[0].units == "pixel") {
                my_annotation.box = box;
            } else {
                my_annotation.box = { 
                    x: Math.round(box.x * ctrl.element.width), 
                    y: Math.round(box.y * ctrl.element.height), 
                    width: Math.round(box.width * ctrl.element.width), 
                    height: Math.round(box.height * ctrl.element.height) 
                };
            }
            my_annotations.push(my_annotation)
        })
        my_annotations = {
            "img": ctrl.img,
            "annotations": my_annotations
        };

        $http.post("/save", my_annotations).then(function (response) {
            processResponse(response);
        }, function (error) {
            console.log(error);
        })
    }

    ctrl.loadNext();
});
