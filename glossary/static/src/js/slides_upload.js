odoo.define('glossary.upload_modal', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var SlidesUpload = require('@website_slides/js/slides_upload')[Symbol.for("default")];

/**
 * Management of the new 'glossary' slide_category
 */
SlidesUpload.SlideUploadDialog.include({
    events: _.extend({}, SlidesUpload.SlideUploadDialog.prototype.events || {}, {
        'change input#glossary_id': '_onChangeGlossary'
        
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

   /**
    * Will automatically set the title of the slide to the title of the chosen glossary
    */
    _onChangeGlossary: function (ev) {
        const $inputElement = this.$("input#name");
        if (ev.added) {
            this.$('.o_error_no_glossary').addClass('d-none');
            this.$('#glossary_id').parent().find('.select2-container').removeClass('is-invalid');
            if (ev.added.text && !$inputElement.val().trim()) {
                $inputElement.val(ev.added.text);
            }
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Overridden to add the "glossary" slide category
     *
     * @override
     * @private
     */
    _setup: function () {
        this._super.apply(this, arguments);
        this.slide_category_data['glossary'] = {
            icon: 'fa-trophy',
            label: _t('Glossary'),
            template: 'website.slide.upload.modal.glossary',
        };
    },
    /**
     * Overridden to add glossarys management in select2
     *
     * @override
     * @private
     */
    _bindSelect2Dropdown: function () {
        this._super.apply(this, arguments);

        var self = this;
        this.$('#glossary_id').select2(this._select2Wrapper(_t('Glossary'), false,
            function () {
                return self._rpc({
                    route: '/slides_survey/glossary/search_read',
                    params: {
                        fields: ['name'],
                    }
                });
            }, 'name')
        );
    },
    /**
     * The select2 field makes the "required" input hidden on the interface.
     * We need to make the "glossary" field required so we override this method
     * to handle validation in a fully custom way.
     *
     * @override
     * @private
     */
    _formValidate: function () {
        var result = this._super.apply(this, arguments);

        var $glossaryInput = this.$('#glossary_id');
        if ($glossaryInput.length !== 0) {
            var $select2Container = $glossaryInput
                .parent()
                .find('.select2-container');
            var $errorContainer = $('.o_error_no_glossary');
            $select2Container.removeClass('is-invalid is-valid');
            if ($glossaryInput.is(':invalid')) {
                $select2Container.addClass('is-invalid');
                $errorContainer.removeClass('d-none');
            } else if ($glossaryInput.is(':valid')) {
                $select2Container.addClass('is-valid');
                $errorContainer.addClass('d-none');
            }
        }

        return result;
    },
    /**
     * Overridden to add the 'glossary' field into the submitted values
     *
     * @override
     * @private
     */
    _getSelect2DropdownValues: function () {
        var result = this._super.apply(this, arguments);

        var glossaryValue = this.$('#glossary_id').select2('data');
//        var certificateValue2 = this.$('#certification_id').select2('data');
        var glossary={};
        if(glossaryValue){
            if(glossaryValue.create){
                glossary.id=false;
                glossary.name=glossaryValue.text;
            }
            else{
                glossary.id=glossaryValue.id;
                
            }
        }
        result['glossary']=glossary;        
        return result;
    },
});

});
