/** @odoo-module **/

//import { useService } from "@web/core/utils/hooks";
//import browser from "@web/core/browser/browser";
//import publicWidget from '@web/legacy/js/public/public_widget';
//
//publicWidget.registry.websiteSlidesSlideToggleIsRequired = publicWidget.Widget.extend({
//    selector: '.o_wslides_js_slide_toggle_is_required',
//    xmlDependencies: ['/website_slides/static/src/xml/slide_management.xml'],
//    events: {
//        'click': '_onRequiredSlideClick',
//    },
//
//    _updateMissingReq: function ($liParent) {
//        var slides = $liParent.closest('.o_wslides_slides_list');
//        var allLi = slides.find('li.o_wslides_slides_list_slide');
//        var missingReq = false;
//        allLi.each(function (){
//            var $slideLink = $(this).find('.o_wslides_js_slides_list_slide_link');
//            var muted = $slideLink.hasClass('text-muted');
//            var slideReq = Boolean($(this).find('.o_wslides_js_slide_toggle_is_required.bh-badge-warning').length);
//            var slideLearned = Boolean($(this).find('.fa-check-circle').length);
//            var isPreview = Boolean($(this).find('.o_wslides_js_slide_toggle_is_preview.badge-success').length);
//            if (missingReq && !isPreview && !muted) {
//                $slideLink.addClass('text-muted');
//            }
//            else if (!missingReq && muted) {
//                $slideLink.removeClass('text-muted');
//            };
//            if (slideReq && !slideLearned) {
//                missingReq = slideReq;
//            };
//        });
//    },
//
//    _toggleSlideRequired: function($slideTarget) {
//        var self = this
//        this.rpc = useService('rpc');
//        this.rpc('/slides/slide/toggle_is_required',
//            {
//                slide_id: $slideTarget.data('slideId')
//            }
//        ).then(function (isRequired) {
//            var $liParent = $slideTarget.closest('li.o_wslides_slides_list_slide');
//            var learned = Boolean($liParent.find('.fa-check-circle').length);
//            if (isRequired) {
//                $slideTarget.removeClass('badge-light badge-hide border text-bg-light');
//                $slideTarget.addClass('bh-badge-warning');
//            } else {
//                $slideTarget.removeClass('bh-badge-warning');
//                $slideTarget.addClass('badge-light badge-hide border text-bg-light');
//            };
//            if (!learned) {
//                self._updateMissingReq($liParent);
//            }
//        });
//    },
//
//    _onRequiredSlideClick: function (ev) {
//        ev.preventDefault();
//        this._toggleSlideRequired($(ev.currentTarget));
//    },
//});
//
//export default {
//    websiteSlidesSlideToggleIsRequired: publicWidget.registry.websiteSlidesSlideToggleIsRequired
//};

import publicWidget from '@web/legacy/js/public/public_widget';
import  useService  from "@web/core/utils/hooks";

publicWidget.registry.websiteSlidesSlideToggleIsRequired = publicWidget.Widget.extend({
    selector: '.o_wslides_js_slide_toggle_is_required',
    events: {
        'click': '_onRequiredSlideClick',
    },

    setup() {
        this._super(...arguments);
        this.rpc =  useService("rpc");
    },

   

    _toggleSlideRequired: function($slideTarget) {
        this.rpc('/slides/slide/toggle_is_required', {
            slide_id: $slideTarget.data('slideId')
        }).then(function (isRequired) {
            var $liParent = $slideTarget.closest('li.o_wslides_slides_list_slide');
            var learned = Boolean($liParent.find('.fa-check-circle').length);
            if (isRequired) {
                $slideTarget.removeClass('badge-light badge-hide border text-bg-light');
                $slideTarget.addClass('bh-badge-warning');
            } else {
                $slideTarget.removeClass('bh-badge-warning');
                $slideTarget.addClass('badge-light badge-hide border text-bg-light');
            };
            if (!learned) {
                var slides = $liParent.closest('.o_wslides_slides_list');
                var allLi = slides.find('li.o_wslides_slides_list_slide');
                var missingReq = false;
                allLi.each(function (){
                    var $slideLink = $(this).find('.o_wslides_js_slides_list_slide_link');
                    var muted = $slideLink.hasClass('text-muted');
                    var slideReq = Boolean($(this).find('.o_wslides_js_slide_toggle_is_required.bh-badge-warning').length);
                    var slideLearned = Boolean($(this).find('.fa-check-circle').length);
                    var isPreview = Boolean($(this).find('.o_wslides_js_slide_toggle_is_preview.badge-success').length);
                    if (missingReq && !isPreview && !muted) {
                        $slideLink.addClass('text-muted');
                    }
                    else if (!missingReq && muted) {
                        $slideLink.removeClass('text-muted');
                    };
                    if (slideReq && !slideLearned) {
                        missingReq = slideReq;
                    };
                });
            }
        });
    },

    _onRequiredSlideClick: function (ev) {
        ev.preventDefault();
        this._toggleSlideRequired($(ev.currentTarget));
    },
});

export default {
    websiteSlidesSlideToggleIsPreview: publicWidget.registry.websiteSlidesSlideToggleIsPreview
};

