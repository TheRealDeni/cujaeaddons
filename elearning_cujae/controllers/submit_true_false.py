from odoo.addons.survey.controllers import main
from odoo import http
from odoo.http import request

class SubmitTrueFalse(main.Survey):
    @http.route('/survey/submit_true_false', type='json', auth='user', methods=['POST'], website=True)
    def submit_true_false(self, respuestas, question_id):
        """
               Procesa las respuestas de preguntas de Verdadero/Falso enviadas desde el frontend.
               """
        user_input = request.env['survey.user_input'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('state', '=', 'in_progress')  # Encuesta en progreso
        ], limit=1)

        if not user_input:
            return {'error': 'No hay una encuesta activa para este usuario.'}

        # Obtiene la pregunta asociada al ID
        question = request.env['survey.question'].sudo().browse(question_id)
        if not question.exists():
            return {'error': 'Pregunta no encontrada.'}

        answers = []

        # Guardar las respuestas
        for respuesta in respuestas:
            inciso_id = respuesta.get('inciso_id')
            valor_respuesta = respuesta.get('respuesta')
            answers.append(valor_respuesta)

            # Validar que el inciso exista
            true_false_item = request.env['survey.true_false_item'].sudo().browse(inciso_id)
            if not true_false_item.exists():
                return {'error': f'El inciso con ID {inciso_id} no existe.'}

        user_input.save_lines(
            question=question,
            answer=answers
        )

        return {'success': True, 'message': 'Respuestas guardadas correctamente'}