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
    }
});
