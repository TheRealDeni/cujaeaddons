from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    score_true_false = fields.Float('Score True False')

    def save_lines(self, question, answer, comment=None):
        if question.question_type != 'true_false':
            return super().save_lines(question, answer, comment)
        elif answer:
            old_answers = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id)
            ])

            #return self._save_line_true_false(question, old_answers, answer)

            items = question.true_false_items
            score_tf = 0
            for i in range(len(answer)):
                if answer[i] == items[i].answer:
                    print('OK')
                    score_tf += items[i].score
            print(score_tf)
            self.score_true_false = score_tf

            self._save_line_true_false(question, old_answers, answer)


    def _save_line_true_false(self, question, old_answers, answers):
        if not (isinstance(answers, list)):
            answers = [answers]

        vals_list = [self._get_line_answer_true_false(question, answer, 'true_false') for answer in answers]

        old_answers.sudo().unlink()
        #return self.env['survey.user_input.line'].create(vals_list)


    def _get_line_answer_true_false(self, question, answer, answer_type):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if answer_type == 'true_false':
            pass
        return vals

    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id',
                 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        for user_input in self:
            # sum(multi-choice question scores) + sum(simple answer_type scores)
            total_possible_score = 0
            for question in user_input.predefined_question_ids:
                if question.question_type == 'simple_choice':
                    total_possible_score += max(
                        [score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0],
                        default=0)
                elif question.question_type == 'multiple_choice':
                    total_possible_score += sum(
                        score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0)
                elif question.is_scored_question:
                    total_possible_score += question.answer_score

            if total_possible_score == 0:
                user_input.scoring_percentage = 0
                user_input.scoring_total = 0
            else:
                score_total = sum(user_input.user_input_line_ids.mapped('answer_score')) + user_input.score_true_false
                user_input.scoring_total = score_total
                print(score_total)
                score_percentage = (score_total / total_possible_score) * 100
                print(score_percentage)
                user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0
