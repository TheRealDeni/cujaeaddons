from odoo import models, fields, api


class SurveyQuestion(models.Model):
    _inherit= 'survey.question'

    @api.depends('question_type', 'scoring_type', 'answer_date', 'answer_datetime', 'answer_numerical_box', 'suggested_answer_ids.is_correct')
    def _compute_is_scored_question(self):
        
        for question in self:
            if question.question_type == 'text_box':
                question.is_scored_question = True
            elif question.question_type == 'date':
                question.is_scored_question = bool(question.answer_date)
            elif question.question_type == 'datetime':
                question.is_scored_question = bool(question.answer_datetime)
            elif question.question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.question_type in ['simple_choice', 'multiple_choice']:
                question.is_scored_question = any(question.suggested_answer_ids.mapped('is_correct'))
            else:
                question.is_scored_question = False
       
            
       


    