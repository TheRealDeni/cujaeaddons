odoo.define('elearning_cujae.upload_modal', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var SlidesUpload = require('@website_slides/js/slides_upload')[Symbol.for("default")];

/**
 * Management of the new 'exam' slide_category
 */
SlidesUpload.SlideUploadDialog.include({
    events: _.extend({}, SlidesUpload.SlideUploadDialog.prototype.events || {}, {
        'change input#exam_id': '_onChangeExam'
        
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

   /**
    * Will automatically set the title of the slide to the title of the chosen exam
    */
    _onChangeExam: function (ev) {
        const $inputElement = this.$("input#name");
        if (ev.added) {
            this.$('.o_error_no_exam').addClass('d-none');
            this.$('#exam_id').parent().find('.select2-container').removeClass('is-invalid');
            if (ev.added.text && !$inputElement.val().trim()) {
                $inputElement.val(ev.added.text);
            }
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Overridden to add the "exam" slide category
     *
     * @override
     * @private
     */
    _setup: function () {
        this._super.apply(this, arguments);
        this.slide_category_data['exam'] = {
            icon: 'fa-trophy',
            label: _t('Exam'),
            template: 'website.slide.upload.modal.another_template',
        };
    },
    /**
     * Overridden to add exams management in select2
     *
     * @override
     * @private
     */
    _bindSelect2Dropdown: function () {
        this._super.apply(this, arguments);

        var self = this;
        this.$('#exam_id').select2(this._select2Wrapper(_t('Exam'), false,
            function () {
                return self._rpc({
                    route: '/slides_survey/exam/search_read',
                    params: {
                        fields: ['title'],
                    }
                });
            }, 'title')
        );
    },
    /**
     * The select2 field makes the "required" input hidden on the interface.
     * We need to make the "exam" field required so we override this method
     * to handle validation in a fully custom way.
     *
     * @override
     * @private
     */
    _formValidate: function () {
        var result = this._super.apply(this, arguments);

        var $examInput = this.$('#exam_id');
        if ($examInput.length !== 0) {
            var $select2Container = $examInput
                .parent()
                .find('.select2-container');
            var $errorContainer = $('.o_error_no_exam');
            $select2Container.removeClass('is-invalid is-valid');
            if ($examInput.is(':invalid')) {
                $select2Container.addClass('is-invalid');
                $errorContainer.removeClass('d-none');
            } else if ($examInput.is(':valid')) {
                $select2Container.addClass('is-valid');
                $errorContainer.addClass('d-none');
            }
        }

        return result;
    },
    /**
     * Overridden to add the 'exam' field into the submitted values
     *
     * @override
     * @private
     */
    _getSelect2DropdownValues: function () {
        var result = this._super.apply(this, arguments);

        var certificateValue = this.$('#exam_id').select2('data');
        var certificateValue2 = this.$('#certification_id').select2('data');
        var survey = {};
        var asd=1;
        if (certificateValue) {
            console.log("primer IF")
            asd=2;
            if (certificateValue.create) {
                survey.id = false;
                survey.title = certificateValue.text;
            } else {
                survey.id = certificateValue.id;
            }
            console.log(survey.id)
        }
        console.log(survey)        
        if (survey.id === undefined) {           
            console.log("segundo IF")
            if (certificateValue2.create) {
                survey.id = false;
                survey.title = certificateValue2.text;
            } else {
                survey.id = certificateValue2.id;
            }
        }     
        result['survey'] = survey;   
        console.log(survey)
        return result;
    },
});

});
