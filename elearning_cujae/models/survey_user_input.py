from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    def save_lines(self, question, answer, comment=None):
        if question.question_type != 'true_false':
            return super().save_lines(question, answer, comment)
        elif answer:
            items = question.true_false_items
            for i in range(len(answer)):
                if answer[i] == items[i].answer:
                    print('BIENN')
                else:
                    print('FATAAALLL')

            old_answers = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id), ])

            self._save_line_true_false(question, old_answers, answer)

    def _save_line_true_false(self, question, old_answers, answers):
        if not (isinstance(answers, list)):
            answers = [answers]

        vals_list = [self._get_line_answer_true_false(question, answer, 'suggestion') for answer in answers]

        old_answers.sudo().unlink()
        #return self.env['survey.user_input.line'].create(vals_list)

    def _get_line_answer_true_false(self, question, answer, answer_type):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'user_answer': answer,
            'skipped': False,
            'answer_type': answer_type,
        }
        return vals

    def validate_true_false_answers(self):
        for line in self.user_input_line_ids:
            if line.question_id.question_type == 'true_false' and line.true_false_item_id:
                print('Verificando')
                line.is_correct = (
                        line.true_false_item_id.answer == line.user_answer
                )
