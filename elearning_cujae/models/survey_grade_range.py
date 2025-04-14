from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SurveyGradeRange(models.Model):
    _name = 'survey.grade.range'
    _description = 'Survey Grade Range'

    survey_id = fields.Many2one('survey.survey', string="Survey", ondelete='cascade')
    min_percentage = fields.Float(string="Minimum Percentage", required=True)
    max_percentage = fields.Float(string="Maximum Percentage", required=True)
    grade = fields.Integer(string="Grade", required=True)

    @api.constrains('min_percentage', 'max_percentage', 'survey_id')
    def _check_ranges(self):
        for record in self:
            # Verificar que el mínimo sea menor que el máximo
            if record.min_percentage >= record.max_percentage:
                raise UserError("El porcentaje mínimo debe ser menor que el porcentaje máximo.")

            # Verificar que no haya solapamiento con otros rangos
            overlapping_ranges = self.search([
                ('survey_id', '=', record.survey_id.id),
                ('id', '!=', record.id),
                ('min_percentage', '<', record.max_percentage),
                ('max_percentage', '>', record.min_percentage),
            ])
            if overlapping_ranges:
                raise UserError("Los rangos de porcentajes no pueden solaparse.")

            # Verificar que los rangos estén dentro de 0% a 100%
            if record.min_percentage < 0 or record.max_percentage > 100:
                raise UserError("Los porcentajes deben estar entre 0% y 100%.")

    @api.constrains('grade', 'survey_id')
    def _check_grade(self):
        for record in self:
            # Verificar que el grado sea un entero
            if not isinstance(record.grade, int):
                raise ValidationError("El grado debe ser un número entero.")

            # Verificar que el grado esté entre 2 y 5
            if not 2 <= record.grade <= 5:
                raise ValidationError("El grado debe estar entre 2 y 5.")

            # Verificar que el grado no se repita para la misma encuesta
            existing_grades = self.search([
                ('survey_id', '=', record.survey_id.id),
                ('id', '!=', record.id),
                ('grade', '=', record.grade),
            ])
            if existing_grades:
                raise ValidationError("No puede haber rangos de grado duplicados para la misma encuesta.")

