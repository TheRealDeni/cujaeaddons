from odoo import models, fields, api
class SurveyQuestionValidAnswer(models.Model):
    _name = 'survey.question.valid.answer'
    _description = 'Valid answer for completion questions'

    question_id = fields.Many2one('survey.question', required=True, ondelete='cascade')
    value = fields.Char('Answer', required=True, translate=True)
