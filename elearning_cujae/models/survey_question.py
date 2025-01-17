from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SurveyQuestion(models.Model):
    _inherit= 'survey.question'

    # Nuevos tipos de preguntas
    question_type = fields.Selection(
        selection_add=[
            ('true_false', 'Verdadero o Falso'),
            #('link', 'Enlaza')
            #('clasification', 'Clasificación'),
        ],
    )

    true_false_items = fields.One2many(
        'survey.true_false_item',
        'question_id',
        string='True/False Items',
        help="List of True/False statements for this question.",
    )

    answer_score_calculated = fields.Float(string="Puntaje Calculado", compute='_compute_answer_score_calculated', store=True)

    answer_score = fields.Float('Score', help="Score value for a correct answer to this question.")

    @api.depends('true_false_items.score')
    def _compute_answer_score_calculated(self):
        for question in self:
            if question.question_type == 'true_false':
                score = 0
                for item in question.true_false_items:
                    score += item.score
                question.answer_score_calculated = score
                question.answer_score = score
            else:
                question.answer_score_calculated = 0

    @api.depends('question_type', 'scoring_type', 'answer_date', 'answer_datetime', 'answer_numerical_box')
    def _compute_is_scored_question(self):
        """ Computes whether a question "is scored" or not. Handles following cases:
          - inconsistent Boolean=None edge case that breaks tests => False
          - survey is not scored => False
          - 'date'/'datetime'/'numerical_box' question types w/correct answer => True
            (implied without user having to activate, except for numerical whose correct value is 0.0)
          - 'simple_choice / multiple_choice': set to True even if logic is a bit different (coming from answers)
          - question_type isn't scoreable (note: choice questions scoring logic handled separately) => False
        """
        for question in self:
            print(question.question_type)
            if question.question_type=='text_box' or question.question_type=='upload_file':
                question.is_scored_question = True
                question.scoring_type= 'scoring_with_answers'
                print("hello")
            elif question.question_type == 'date':
                question.is_scored_question = bool(question.answer_date)
            elif question.question_type == 'datetime':
                question.is_scored_question = bool(question.answer_datetime)
            elif question.question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.question_type in ['simple_choice', 'multiple_choice', 'true_false']:  # Add 'text_box' here
                question.is_scored_question = True
            else:
                question.is_scored_question = False
            
    def write(self, vals):
        res = super(SurveyQuestion, self).write(vals)
        for question in self:
            if question.question_type == 'true_false' and not question.true_false_items:
                raise ValidationError("A 'True or False' question must have at least one item.")
        return res


    