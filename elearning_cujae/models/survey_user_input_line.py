from Tools.scripts.dutree import store

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    true_false_item_id = fields.Many2one(
        'survey.true_false_item',
        string="True/False Item"
    )
    user_answer = fields.Selection([
        ('true', 'Verdadero'),
        ('false', 'Falso')
    ], string="User Answer")

    is_correct = fields.Boolean(string="Is Correct", compute='_compute_is_correct', store=True)

    @api.depends('true_false_item_id', 'user_answer')
    def _compute_is_correct(self):
        for line in self:
            print('aqui')
            if line.true_false_item_id:
                print('verificando')
                line.is_correct = (
                        line.true_false_item_id.answer == line.user_answer
                )
