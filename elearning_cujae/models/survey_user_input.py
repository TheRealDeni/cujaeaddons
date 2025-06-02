from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    score_true_false = fields.Float('Score True False')

    grade = fields.Integer(string="Grade", default=2, compute='_compute_grade', store=True)
    professor_check = fields.Boolean(related='survey_id.professor_check', string='Checked by teacher', store=True,
                                     readonly=True)
    checked = fields.Boolean(string='Checked')
    email_sent = fields.Boolean(string='Email Sent', default=False, copy=False)
    is_exam = fields.Boolean(related='survey_id.exam', string='Is an exam', store=True, readonly=True)
    is_certification = fields.Boolean(related='survey_id.certification', string='Is a certification', store=True,
                                      readonly=True)

    def write(self, vals):
        res = super(SurveyUserInput, self).write(vals)
        records_to_send = self.env['survey.user_input']
        for record in self:
            if record.state == 'done' and not record.email_sent:
                if (not record.professor_check) or (record.professor_check and record.checked):
                    records_to_send += record
        if records_to_send:
            records_to_send._send_grade_email()
            records_to_send.write({'email_sent': True})
        return res

    def _send_grade_email(self):
        template = self.env.ref('elearning_cujae.email_template_survey_grade', raise_if_not_found=False)
        if template:
            for record in self:
                template.send_mail(record.id, force_send=True)

    @api.depends('scoring_percentage')
    def _compute_grade(self):
        for user_input in self:
            grade_found = False
            for grade_range in user_input.survey_id.grade_ranges:
                if grade_range.min_percentage <= user_input.scoring_percentage <= grade_range.max_percentage:
                    user_input.grade = grade_range.grade
                    grade_found = True
                    break

            if not grade_found:
                user_input.grade = 2

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
                elif question.question_type == 'link':
                    total_possible_score += sum(
                        score for score in question.mapped('link_items.score') if score > 0)
                elif question.question_type == 'true_false':
                    total_possible_score += sum(
                        score for score in question.mapped('true_false_items.score') if score > 0)
                elif question.is_scored_question:
                    total_possible_score += question.answer_score

            if total_possible_score == 0:
                user_input.scoring_percentage = 0
                user_input.scoring_total = 0
            else:
                score_total = sum(user_input.user_input_line_ids.mapped('answer_score'))
                user_input.scoring_total = score_total
                score_percentage = (score_total / total_possible_score) * 100
                user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0

    def save_lines(self, question, answer, comment=None):
        """Save the user's answer for the given question."""
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id), ])

        print(question)
        print(answer)

        if question.question_type in 'upload_file':
            return self._save_line_file(question, old_answers, answer)
        elif question.question_type in 'link':
            self._save_line_link(question, old_answers, answer)
        elif question.question_type in 'true_false':
            self._save_line_true_false(question, old_answers, answer)
        else:
            return super().save_lines(question, answer, comment)

    def _save_line_link(self, question, old_answers, answers):
        vals_list = []

        for answer in answers:
            link_item_id = answer.get('link_item_id')
            link_item_answer_id = int(answer.get('link_item_answer_id'))
            vals = {
                'user_input_id': self.id,
                'question_id': question.id,
                'answer_type': 'link',
                'link_item_id': link_item_id,
                'link_item_answer_id': link_item_answer_id,
                'skipped': False,
            }
            vals_list.append(vals)


        old_answers.sudo().unlink()
        self.env['survey.user_input.line'].create(vals_list)

    def _save_line_true_false(self, question, old_answers, answers):
        vals_list = []

        for answer in answers:
            true_false_item_id = answer.get('true_false_item_id')
            true_false_item_answer = answer.get('true_false_item_answer')
            vals = {
                'user_input_id': self.id,
                'question_id': question.id,
                'answer_type': 'true_false',
                'true_false_item_id': true_false_item_id,
                'true_false_item_answer': true_false_item_answer,
                'skipped': False,
            }
            vals_list.append(vals)

        old_answers.sudo().unlink()
        self.env['survey.user_input.line'].create(vals_list)

    def _save_line_file(self, question, old_answers, answer):
        """ Save the user's file upload answer for the given question."""
        vals = self._get_line_answer_file_upload_values(question,
                                                        'upload_file', answer)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].create(vals)

    def _get_line_answer_file_upload_values(self, question, answer_type,
                                            answer):
        """Get the values to use when creating or updating a user input line
        for a file upload answer."""
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if answer_type == 'upload_file':
            file_data = answer[0]
            file_name = answer[1]
            attachment_ids = []
            for file in range(len(answer[1])):
                attachment = self.env['ir.attachment'].create({
                    'name': file_name[file],
                    'type': 'binary',
                    'datas': file_data[file],
                    'public': True,
                    'res_model': 'survey.user_input.line',  # Modelo relacionado
                    'res_id': self.id,  # ID de la línea de respuesta
                })
                attachment_ids.append(attachment.id)
            vals['value_file_data_ids'] = attachment_ids
        return vals

    def _prepare_statistics(self):
        res = dict((user_input, {
            'by_section': {}
        }) for user_input in self)

        scored_questions = self.mapped('predefined_question_ids').filtered(lambda question: question.is_scored_question)

        for question in scored_questions:
            if question.question_type in ['simple_choice', 'multiple_choice']:
                question_correct_suggested_answers = question.suggested_answer_ids.filtered(lambda answer: answer.is_correct)
            elif question.question_type == 'link':
                link_items = question.link_items.filtered(lambda link_item: link_item.name)
            elif question.question_type == 'true_false':
                true_false_items = question.true_false_items.filtered(lambda true_false_item: true_false_item.name)

            question_section = question.page_id.title or _('Uncategorized')
            for user_input in self:
                user_input_lines = user_input.user_input_line_ids.filtered(lambda line: line.question_id == question)
                if question.question_type in ['simple_choice', 'multiple_choice']:
                    answer_result_key = super(SurveyUserInput, self)._choice_question_answer_result(user_input_lines, question_correct_suggested_answers)
                elif question.question_type == 'link':
                    answer_result_key = self._link_question_answer_result(user_input_lines, link_items)
                elif question.question_type == 'true_false':
                    answer_result_key = self._true_false_question_answer_result(user_input_lines, true_false_items)
                else:
                    answer_result_key = super(SurveyUserInput, self)._simple_question_answer_result(user_input_lines)

                if question_section not in res[user_input]['by_section']:
                    res[user_input]['by_section'][question_section] = {
                        'question_count': 0,
                        'correct': 0,
                        'partial': 0,
                        'incorrect': 0,
                        'skipped': 0,
                    }

                res[user_input]['by_section'][question_section]['question_count'] += 1
                res[user_input]['by_section'][question_section][answer_result_key] += 1

        for user_input in self:
            correct_count = 0
            partial_count = 0
            incorrect_count = 0
            skipped_count = 0

            for section_counts in res[user_input]['by_section'].values():
                correct_count += section_counts.get('correct', 0)
                partial_count += section_counts.get('partial', 0)
                incorrect_count += section_counts.get('incorrect', 0)
                skipped_count += section_counts.get('skipped', 0)

            res[user_input]['totals'] = [
                {'text': _("Correct"), 'count': correct_count},
                {'text': _("Partially"), 'count': partial_count},
                {'text': _("Incorrect"), 'count': incorrect_count},
                {'text': _("Unanswered"), 'count': skipped_count}
            ]

        return res

    def _link_question_answer_result(self, user_input_lines, link_items):
        correct_user_input_lines = user_input_lines.filtered(lambda line: line.answer_is_correct and not line.skipped).mapped('link_item_id')
        incorrect_user_input_lines = user_input_lines.filtered(lambda line: not line.answer_is_correct and not line.skipped)
        if link_items and correct_user_input_lines == link_items:
            return 'correct'
        elif correct_user_input_lines and correct_user_input_lines < link_items:
            return 'partial'
        elif not correct_user_input_lines and incorrect_user_input_lines:
            return 'incorrect'
        else:
            return 'skipped'

    def _true_false_question_answer_result(self, user_input_lines, true_false_items):
        correct_user_input_lines = user_input_lines.filtered(lambda line: line.answer_is_correct and not line.skipped).mapped('true_false_item_id')
        incorrect_user_input_lines = user_input_lines.filtered(lambda line: not line.answer_is_correct and not line.skipped)
        if true_false_items and correct_user_input_lines == true_false_items:
            return 'correct'
        elif correct_user_input_lines and correct_user_input_lines < true_false_items:
            return 'partial'
        elif not correct_user_input_lines and incorrect_user_input_lines:
            return 'incorrect'
        else:
            return 'skipped'

    def mark_as_checked(self):
        self.checked = True