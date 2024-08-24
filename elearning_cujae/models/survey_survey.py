from odoo import models, fields, api

class Survey(models.Model):
    _inherit="survey.survey"
    exam = fields.Boolean('Is an Exam', compute='_compute_exam',readonly=False, store=True, precompute=True)
    exam_give_badge = fields.Boolean('Give exam Badge', compute='_compute_exam_give_badge',readonly=False, store=True, copy=False)
    exam_badge_id = fields.Many2one('gamification.badge', 'Exam Badge', copy=False)
    exam_badge_id_dummy = fields.Many2one(related='exam_badge_id', string='Exam Badge ')
    @api.depends('scoring_type')
    def _compute_exam(self):
        for survey in self:
            if not survey.exam or survey.scoring_type == 'no_scoring':
                survey.exam = False
    
    @api.depends('users_login_required', 'exam')
    def _compute_exam_give_badge(self):
        for survey in self:
            if not survey.exam_give_badge or \
               not survey.users_login_required or \
               not survey.exam:
                survey.exam_give_badge = False 