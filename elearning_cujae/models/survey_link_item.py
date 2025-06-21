from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SurveyLinkItem(models.Model):
    _name = 'survey.link_item'
    _description = 'Link Question Item'

    name = fields.Char(string='Pregunta', help="La orden de la pregunta, puede dejarse en blanco y poner "
                                               "solamente una respuesta que no pertenecerá a ninguna pregunta")
    answer = fields.Char(string='Respuesta', required=True, help="La respuesta a una pregunta dada o respuesta de "
                                                                 "relleno en caso de que no se ponga una pregunta")
    score = fields.Float(string="Puntuación", required=True, default=0, help="La puntuación de este inciso")
    question_id = fields.Many2one(
        'survey.question',
        string='Parent Question',
        ondelete='cascade',
        required=True,
        default=lambda self: self._context.get('active_id'),
    )

    @api.constrains('score')
    def _check_score(self):
        for record in self:
            if record.score < 0:
                raise ValidationError(_("La puntuación no puede ser negativa"))
