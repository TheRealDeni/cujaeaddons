odoo.define('glossary.fullscreen', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];
    var ajax = require('web.ajax');

    Fullscreen.include({
        _renderSlide: function () {
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');

            if (this.get('slide').category === "glossary") {
                var slideId = this.get('slide').id;
                console.log(this.get('slide'));    
                
                // Hacer una llamada AJAX para obtener los términos del glosario
                return ajax.rpc('/slide/get_glossary_url', { slide_id: slideId }).then(function (data) {
                    // Renderizar la plantilla con los datos recibidos
                    $content.html(QWeb.render('website.slides.fullscreen.glossary', { widget: this, terms: data.terms, glossary: data.glossary }));

                    // Marcar el slide como completado
                    return ajax.rpc('/slide/complete_slide', { slide_id: slideId });
                }.bind(this)).then(function () {
                    // Actualizar el atributo completed del slide en el cliente
                    this.get('slide').completed = true;
                }.bind(this));
            }

            return Promise.all([def]);
        },
        
    });
});
