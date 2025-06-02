from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SurveyTrueFalseItem(models.Model):
    _name = 'survey.true_false_item'
    _description = 'True/False Question Item'

    name = fields.Char(string='Pregunta', required=True, help="The statement for this item.")
    answer = fields.Selection(
        [('V', 'V'), ('F', 'F')],
        string='Respuesta correcta',
        required=True,
        help="Respuesta correcta para esta pregunta"
    )
    score = fields.Float(string="Puntuación", required=True, default=0, help="La puntuación de este inciso")
    question_id = fields.Many2one(
        'survey.question',
        string='Parent Question',
        ondelete='cascade',
        required=True,
        help="The question this item belongs to.",
        default=lambda self: self._context.get('active_id')
    )

    @api.constrains('score')
    def _check_score(self):
        for rec in self:
            if rec.score <= 0:
                raise ValidationError(_("La puntuación debe ser mayor que 0"))
