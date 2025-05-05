from odoo import api, fields, models

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    grade = fields.Integer(string="Grade",default=2, compute='_compute_grade', store=True)
    professor_check = fields.Boolean(related='survey_id.professor_check', string='Revisado por el profesor', store=True, readonly=True)
    checked= fields.Boolean(string='Checked')
    email_sent = fields.Boolean(string='Email Sent', default=False, copy=False)

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
        if question.question_type in 'upload_file':
            res = self._save_line_file(question, old_answers, answer)
        else:
            res = super().save_lines(question, answer, comment)
        return res

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
           