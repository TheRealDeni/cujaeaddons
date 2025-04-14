from odoo import models, fields, api

class Survey(models.Model):
    _inherit="survey.survey"
    grade_ranges = fields.One2many('survey.grade.range', 'survey_id', string="Grade Ranges")
    exam = fields.Boolean('¿Es un examen?', compute='_compute_exam',readonly=False, store=True, precompute=True)
    exam_give_badge = fields.Boolean('Dar insignia de examen', compute='_compute_exam_give_badge',readonly=False, store=True, copy=False)
    exam_badge_id = fields.Many2one('gamification.badge', 'Insignia de examen', copy=False)
    exam_badge_id_dummy = fields.Many2one(related='exam_badge_id', string='Insignia de examen ')
    professor_check= fields.Boolean('Revisado por profesor', compute='_compute_check_survey',store=True)
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

    @api.depends('question_ids')
    def _compute_check_survey(self):
        flag=False
        for survey in self:
            survey.professor_check = False
            for question in survey.question_ids:
                if question.question_type in ('text_box', 'upload_file') and question.is_scored_question and flag==False:
                    survey.professor_check = True
                    flag=True
                    
