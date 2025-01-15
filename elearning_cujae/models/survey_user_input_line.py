from Tools.scripts.dutree import store

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    answer_type = fields.Selection(
        selection_add=[
            ('true_false', 'Verdadero o Falso'),
        ],
    )

    true_false_item_id = fields.Many2one(
        'survey.true_false_item',
        string="True/False Item"
    )
