from odoo import models, fields, api

class Survey(models.Model):
    _inherit="survey.survey"
    exam = fields.Boolean('Is an Exam', compute='_compute_exam',readonly=False, store=True, precompute=True)
    @api.depends('scoring_type')
    def _compute_exam(self):
        for survey in self:
            if not survey.exam or survey.scoring_type == 'no_scoring':
                survey.exam = False