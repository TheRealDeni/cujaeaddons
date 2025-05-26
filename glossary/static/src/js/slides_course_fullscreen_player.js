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
                
                return ajax.rpc('/slide/get_glossary_url', { 
                    slide_id: slideId 
                }).then(function (data) {
                    $content.html(QWeb.render('website.slides.fullscreen.glossary', {
                        widget: this,
                        groups: data.groups,
                        glossary: data.glossary
                    }));
                    
                    this._initAccordions(); // Inicializar acordeones
                    
                    return ajax.rpc('/slide/complete_slide', { 
                        slide_id: slideId 
                    });
                }.bind(this)).then(function () {
                    this.get('slide').completed = true;
                }.bind(this));
            }

            return Promise.all([def]);
        },

        _initAccordions: function() {
            // Inicializar acordeones usando jQuery (Bootstrap)
            $('.accordion .collapse').collapse({
                toggle: false
            });
        }
    });
});