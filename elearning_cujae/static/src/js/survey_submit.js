/** @odoo-module **/

import SurveyFormWidget from 'survey.form';

SurveyFormWidget.include({

    /**
     * Extiende la lógica de preparación de respuestas.
     */
    _prepareSubmitValues: function (formData, params) {
        var self = this;
        formData.forEach(function (value, key) {
            switch (key) {
                case 'csrf_token':
                case 'token':
                case 'page_id':
                case 'question_id':
                    params[key] = value;
                    break;
            }
        });
        // Get all question answers by question type
        this.$('[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'text_box':
                case 'char_box':
                case 'numerical_box':
                    params[this.name] = this.value;
                    break;
                case 'date':
                    params = self._prepareSubmitDates(params, this.name, this.value, false);
                    break;
                case 'datetime':
                    params = self._prepareSubmitDates(params, this.name, this.value, true);
                    break;
                case 'simple_choice_radio':
                case 'multiple_choice':
                    params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                    break;
                case 'matrix':
                    params = self._prepareSubmitAnswersMatrix(params, $(this));
                    break;
                case 'link':  // Tu tipo de pregunta personalizada
                    params = self._prepareSubmitLink(params, $(this), $(this).data('name'));
                    break;
                case 'true_false':
                    params = self._prepareSubmitTrueFalse(params, $(this), $(this).data('name'));
                    break;
            }
        });
    },

    /**
     * Prepara los valores de una pregunta tipo "link"
     */
    _prepareSubmitLink: function (params, parent, questionId) {
        var self = this;
        // Recorremos todos los dropdowns vinculados a incisos
        parent.find('.o_survey_link_dropdown').each(function () {
            const itemId = $(this).closest('.o_survey_link_item').data('item-id');
            const answerId = $(this).val();
            if (itemId && answerId) {
                if (!params[questionId]) {
                    params[questionId] = [];
                }
                params[questionId].push({
                    'link_item_id': itemId,
                    'link_item_answer_id': answerId,
                });
            }
        });
        return params;
    },

    /**
     * Prepara los valores de una pregunta tipo "true_false"
     */
    _prepareSubmitTrueFalse: function (params, parent, questionId) {
        var self = this;
        // Recorremos todos los dropdowns vinculados a incisos
        parent.find('.o_survey_true_false_dropdown').each(function () {
            const itemId = $(this).closest('.o_survey_true_false_item').data('item-id');
            const trueFalseAnswer = $(this).val();
            if (itemId && trueFalseAnswer) {
                if (!params[questionId]) {
                    params[questionId] = [];
                }
                params[questionId].push({
                    'true_false_item_id': itemId,
                    'true_false_item_answer': trueFalseAnswer,
                });
            }
        });
        return params;
    },


});
