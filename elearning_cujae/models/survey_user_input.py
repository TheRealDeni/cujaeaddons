from odoo import api, fields, models

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    grade = fields.Integer(string="Grade",default=2, compute='_compute_grade', store=True)
    professor_check = fields.Boolean(related='survey_id.professor_check', string='Revisado por el profesor', store=True, readonly=True)
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
            print("la nota eeeeeeeeeeeeeeeeeeeeees")
            print(self.grade)
            print(self.survey_id)
            print(self.professor_check)