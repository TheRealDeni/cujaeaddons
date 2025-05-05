/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import publicWidget from '@web/legacy/js/public/public_widget';
import Fullscreen from '@website_slides/js/slides_course_fullscreen_player';
import { useService } from "@web/core/utils/hooks";

var getReqSlide = function (obj, slideId){
    return new Promise((resolve, reject) => {
        $.ajax({
          url: '/slides/slide/required_slide',
          type: 'GET',
          data: { slide_id: slideId },
          dataType: 'json',
          success: function(data) {
            resolve(data);
          },
          error: function(xhr, status, error) {
            reject(new Error('Error al obtener el slide requerido.', error));
          }
        });
      });
}

publicWidget.registry.websiteSlidesSlidePreventLearningAdmin = publicWidget.Widget.extend({
    selector: '.o_wslides_js_slides_list_slide_link,.o_wslides_lesson_aside_list_link a,.next-slide-link',
    xmlDependencies: ['/website_slides/static/src/xml/website_slides_upload.xml'],
    events: {
        'click': '_onMissingRequirementSlideClick',
    },

    setup() {
        this._super(...arguments);
        this.rpc =  useService("rpc");
    },

    _onMissingRequirementSlideClick: async function (ev) {
        console.log('_onMissingRequirementSlideClick');
        ev.stopPropagation();
        ev.preventDefault();
        var dataId = $(ev.currentTarget).data('id');
        var slideHref = $(ev.currentTarget).attr('href')
        if (dataId) {var slideId = parseInt(dataId)}
        else {
            var slideLink = slideHref.replace('?fullscreen=1', '');
            var slideSplit = slideLink.split('-');
            var slideId = parseInt(slideSplit[slideSplit.length - 1]);
        }
        const reqSlide = await getReqSlide(this, slideId);
        console.log('reqSlide: ', reqSlide);
        if (reqSlide && !reqSlide.can_skip) {
            console.log('cant skip');
            var url = reqSlide.url;
            if (slideHref.includes('?fullscreen=1')) {url = url + '?fullscreen=1'}
            $("#modal_required_slide").attr('href', url);
            $("#modal_required_slide").html(reqSlide.name);
            $("#missing_requirement_modal").modal('show');
        }
        else if (slideHref) {location.href = slideHref;}
    },
});

var BHSidebar = publicWidget.Widget.extend({
    events: {
        "click .o_wslides_fs_sidebar_list_item": '_onClickTab',
        "click .o_wslides_fs_slide_link": '_onClickLink',
//            "click #modal_required_slide": '_onClickModalLink',
    },
    init: function (parent, slideList, defaultSlide) {
        var result = this._super.apply(this, arguments);
        this.slideEntries = slideList;
        this.set('slideEntry', defaultSlide);
        this.rpc =  useService("rpc");
        return result;
    },
    start: function (){
        var self = this;
        this.on('change:slideEntry', this, this._onChangeCurrentSlide);
        return this._super.apply(this, arguments).then(function (){
            $(document).keydown(self._onKeyDown.bind(self));
        });
    },
    destroy: function () {
        $(document).unbind('keydown', this._onKeyDown.bind(this));
        return this._super.apply(this, arguments);
    },
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    openRequiredSlideModal: function (reqSlide) {
        var self = this;
        $("#modal_required_slide").attr('data-id', reqSlide.id);
        $("#modal_required_slide span").html(reqSlide.name);
        $("#missing_requirement_modal").modal('show');
        $("#modal_required_slide").click(function () {
            var slide = findSlide(self.slideEntries, {id: reqSlide.id, isQuiz: false});
            self.set('slideEntry', slide);
            $("#missing_requirement_modal").modal('hide');
        });
    },

    /**
     * Change the current slide with the next one (if there is one).
     *
     * @public
     */
    goNext: async function () {
        var currentIndex = this._getCurrentIndex();
        if (currentIndex < this.slideEntries.length-1) {
            var nextSlide = this.slideEntries[currentIndex+1];
            const reqSlide = await getReqSlide(this, nextSlide.id);
            if (reqSlide && !reqSlide.can_skip) {this.openRequiredSlideModal(reqSlide)}
            else {this.set('slideEntry', nextSlide);}
        }
    },
    /**
     * Change the current slide with the previous one (if there is one).
     *
     * @public
     */
    goPrevious: function () {
        var currentIndex = this._getCurrentIndex();
        if (currentIndex >= 1) {
            this.set('slideEntry', this.slideEntries[currentIndex-1]);
        }
    },
    /**
     * Greens up the bullet when the slide is completed
     *
     * @public
     * @param {Integer} slideId
     */
    setSlideCompleted: async function (slideId) {
        var $elem = this.$('.fa-circle-thin[data-slide-id="'+slideId+'"],.fa-lock[data-slide-id="'+slideId+'"]');
        $elem.removeClass('fa-circle-thin').removeClass('fa-lock').addClass('fa-check text-success o_wslides_slide_completed');

        const reqSlide = await getReqSlide(this, slideId);
        if (!reqSlide) {this.updateRequirement()}
    },
    /**
     * Updates the progressbar whenever a lesson is completed
     *
     * @public
     * @param {*} channelCompletion
     */
    updateProgressbar: function (channelCompletion) {
        var completion = Math.min(100, channelCompletion);
        this.$('.progress-bar').css('width', completion + "%" );
        this.$('.o_wslides_progress_percentage').text(completion);
    },

    updateRequirement: function () {
        var self = this;
        var allSlides = this.slideEntries;
        var nextSlides = allSlides.slice(this._getCurrentIndex() + 1, allSlides.length - 1);
        for (const slide of nextSlides) {
            var slideId = slide.id;
            var $slideName = self.$('li[data-id="'+slideId+'"] div.o_wslides_fs_slide_name');
            var $slideLink = self.$('li[data-id="'+slideId+'"] a.o_wslides_fs_slide_link');
            $slideName.removeClass('text-600');
            $slideLink.removeClass('text-600');
            if (slide.hasQuestion && !slide.isQuiz) {
                var $slideQuiz = self.$('li[data-id="'+slideId+'"] a.o_wslides_fs_slide_quiz');
                $slideQuiz.removeClass('text-600');
            };
            if (slide.required === 'True') {break}
            };
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Get the index of the current slide entry (slide and/or quiz)
     */
//    _getCurrentIndex: function () {
//        var slide = this.get('slideEntry');
//        var currentIndex = this.slideEntries.findIndex(entry =>{
//            return entry.id === slide.id && entry.isQuiz === slide.isQuiz;
//        });
//        return currentIndex;
//    },
    //--------------------------------------------------------------------------
    // Handler
    //--------------------------------------------------------------------------
    /**
     * Handler called whenever the user clicks on a sub-quiz which is linked to a slide.
     * This does NOT handle the case of a slide of type "quiz".
     * By going through this handler, the widget will be able to determine that it has to render
     * the associated quiz and not the main content.
     *
     * @private
     * @param {*} ev
     */
    _onClickMiniQuiz: function (ev){
        var slideID = parseInt($(ev.currentTarget).data().slide_id);
        this.set('slideEntry',{
            slideID: slideID,
            isMiniQuiz: true
        });
        this.trigger_up('change_slide', this.get('slideEntry'));
    },

    /**
     * Handler called when the user clicks on a normal slide tab
     *
     * @private
     * @param {*} ev
     */
    _onClickTab: async function (ev) {
        ev.stopPropagation();
        var self = this;
        var $elem = $(ev.currentTarget);
        var slideID = parseInt($elem.data('id'));
        console.log('aaaa');
        const reqSlide = await getReqSlide(this, slideID);
        if ($elem.data('canAccess') === 'True') {
            if (!reqSlide || (reqSlide && reqSlide.can_skip)) {
                var isQuiz = $elem.data('isQuiz');
                var slide = findSlide(this.slideEntries, {id: slideID, isQuiz: isQuiz});
                this.set('slideEntry', slide);
            }
            else {this.openRequiredSlideModal(reqSlide)};
        }
    },

    _onClickLink: async function (ev) {
        ev.preventDefault();
        var self = this;
        var $elem = $(ev.currentTarget);
        var $slideElem = $elem.closest('li.o_wslides_fs_sidebar_list_item');
        var slideID = parseInt($slideElem.data('id'));
        const reqSlide = await getReqSlide(this, slideID);
        if ($slideElem.data('canAccess') === 'True') {
            if (!reqSlide || (reqSlide && reqSlide.can_skip)) {
                window.open($elem.attr('href'), '_blank').focus();
            }
            else {this.openRequiredSlideModal(reqSlide)};
        }
    },

    /**
     * Actively changes the active tab in the sidebar so that it corresponds
     * the slide currently displayed
     *
     * @private
     */
    _onChangeCurrentSlide: function () {
        var slide = this.get('slideEntry');
        this.$('.o_wslides_fs_sidebar_list_item.active').removeClass('active');
        var selector = '.o_wslides_fs_sidebar_list_item[data-id='+slide.id+'][data-is-quiz!="1"]';

        this.$(selector).addClass('active');
        this.trigger_up('change_slide', this.get('slideEntry'));
    },

    /**
     * Binds left and right arrow to allow the user to navigate between slides
     *
     * @param {*} ev
     * @private
     */
    _onKeyDown: function (ev){
        switch (ev.key){
            case "ArrowLeft":
                this.goPrevious();
                break;
            case "ArrowRight":
                this.goNext();
                break;
        }
    },
});

//var findSlide = function (slideList, matcher) {
//    var slideMatch = _.matcher(matcher);
//    return _.find(slideList, slideMatch);
//};

/**
 * Helper: Get the slide dict matching the given criteria
 *
 * @private
 * @param {Array<Object>} slideList List of dict reprensenting a slide
 * @param {[string] : any} matcher
 */
var findSlide = function (slideList, matcher) {
    return slideList.find((slide) => {
        return Object.keys(matcher).every((key) => matcher[key] === slide[key]);
    });
};

var ShareButton = publicWidget.Widget.extend({
    events: {
        "click .o_wslides_fs_share": '_onClickShareSlide'
    },

    init: function (el, slide) {
        var result = this._super.apply(this, arguments);
        this.slide = slide;
        this.rpc =  useService("rpc");
        return result;
    },

    _openDialog: function() {
        return new ShareDialog(this, {}, this.slide).open();
    },

    _onClickShareSlide: function (ev) {
        ev.preventDefault();
        this._openDialog();
    },

    _onChangeSlide: function (currentSlide) {
        this.slide = currentSlide;
    }

});

var BHFullscreen = Fullscreen.include({
    init: function (parent, slides, defaultSlideId, channelData) {
        var result = this._super.apply(this,arguments);
        this.initialSlideID = defaultSlideId;
        this.slides = this._preprocessSlideData(slides);
        this.channel = channelData;
        var slide;
        const urlParams = new URL(window.location).searchParams;
        if (defaultSlideId) {
            slide = findSlide(this.slides, {id: defaultSlideId, isQuiz: String(urlParams.get("quiz")) === "1" });
        } else {
            slide = this.slides[0];
        }

        this.set('slide', slide);

        this.sidebar = new BHSidebar(this, this.slides, slide);
        this.shareButton = new ShareButton(this, slide);
        return result;
    },
});

export default {
    websiteSlidesSlidePreventLearningAdmin: publicWidget.registry.websiteSlidesSlidePreventLearningAdmin
};
