/** @odoo-module **/

import SurveyFormWidget from 'survey.form';

SurveyFormWidget.include({

    _onSubmit: function(event) {
        event.preventDefault();
        var self = this;
        let container = self.$el; //
        let questionContainer = container.find('[id*="vf_question_container_"]');
        let respuestas = [];
        let incisos = container.find('.vf-item');
        if(incisos.length > 0){
            incisos.each(function() {
                let incisoId = $(this).data('inciso-id');
                let respuesta = $(this).find('select').val();
                respuestas.push({
                    'inciso_id': incisoId,
                    'respuesta': respuesta
                });
            });
            self._rpc({
                route: '/survey/submit_true_false',
                params: {
                    'respuestas': respuestas,
                    'question_id': parseInt(questionContainer.attr('id').replace("vf_question_container_",""))
                },
            }).then(function(data){
                console.log("Respuesta del servidor:",data);
            });
        }
        return this._super.apply(this, arguments);
    },

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


});
