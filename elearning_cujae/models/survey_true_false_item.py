from odoo import models, fields

class SurveyTrueFalseItem(models.Model):
    _name = 'survey.true_false_item'
    _description = 'True/False Question Item'

    name = fields.Char(string='Pregunta', required=True, help="The statement for this item.")
    answer = fields.Selection(
        [('true', 'V'), ('false', 'F')],
        string='Respuesta correcta',
        required=True,
        help="Respuesta correcta para esta pregunta"
    )
    student_answer = fields.Selection(
        [('true', 'V'), ('false', 'F')],
        string='Respuesta del estudiante',
        help="La respuesta del estudiante para esta pregunta"
    )
    question_id = fields.Many2one(
        'survey.question',
        string='Parent Question',
        ondelete='cascade',
        required=True,
        help="The question this item belongs to.",
        default=lambda self: self._context.get('active_id')
    )
