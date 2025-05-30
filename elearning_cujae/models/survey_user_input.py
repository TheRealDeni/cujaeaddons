from odoo import api, fields, models
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
            if answer:
                print('Es Verdadero o Falso')
                print(answer)
                items = question.true_false_items
                score_tf = 0
                for i in range(len(answer)):
                    if answer[i] == items[i].answer:
                        score_tf += items[i].score
                self.score_true_false = score_tf
        else:
            return super().save_lines(question, answer, comment)

    def _save_line_link(self, question, old_answers, answers):
        # Limpiar respuestas anteriores
        old_answers.sudo().unlink()
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

        if vals_list:
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

    def mark_as_checked(self):
        self.checked = True