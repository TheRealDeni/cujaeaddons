from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class Channel(models.Model):
    _inherit = 'slide.channel'

    nbr_exam = fields.Integer("Número de exámenes", compute='_compute_slides_statistics', store=True)
    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)
    availability_start_date = fields.Datetime(string="Fecha de Inicio de Disponibilidad", default=fields.Datetime.now)  # Cambio a Datetime
    availability_end_date = fields.Datetime(string="Fecha de Fin de Disponibilidad")  # Cambio a Datetime

    @api.model
    def _cron_check_course_availability(self):
        """
        Función que se ejecuta diariamente mediante un cron job para verificar la disponibilidad de los cursos.
        Actualiza el campo 'is_published' basándose en las fechas de disponibilidad.
        """
        now = datetime.now()  # Usamos datetime.now() para incluir la hora actual
        courses = self.search([])  # Busca todos los cursos (slide.channel)
        for course in courses:
            if course.availability_start_date and course.availability_end_date:
                if course.availability_start_date <= now <= course.availability_end_date:
                    if not course.is_published:
                        course.write({'is_published': True})
                else:
                    if course.is_published:
                        course.write({'is_published': False})
            elif course.availability_start_date: #Solo fecha de inicio
                if course.availability_start_date <= now:
                    if not course.is_published:
                        course.write({'is_published': True})
                else:
                    if course.is_published:
                        course.write({'is_published': False})
            elif course.availability_end_date: #Solo fecha de fin
                if now <= course.availability_end_date:
                    if not course.is_published:
                        course.write({'is_published': True})
                else:
                    if course.is_published:
                        course.write({'is_published': False})


    @api.constrains('availability_start_date', 'availability_end_date')
    def _check_availability_dates(self):
        """
        Validación para asegurar que la fecha de inicio no sea posterior a la fecha de fin.
        """
        for record in self:
            if record.availability_start_date and record.availability_end_date and record.availability_start_date > record.availability_end_date:
                raise UserError("La fecha de inicio de disponibilidad no puede ser posterior a la fecha de fin.")


    @api.onchange('availability_start_date', 'availability_end_date')
    def _onchange_availability_dates(self):
        """
        Actualiza el estado de 'is_published' cuando cambian las fechas de disponibilidad directamente en el formulario.
        """
        now = datetime.now() # Usamos datetime.now() para incluir la hora actual
        if self.availability_start_date and self.availability_end_date:
            if self.availability_start_date <= now <= self.availability_end_date:
                self.is_published = True
            else:
                self.is_published = False
        elif self.availability_start_date: #Solo fecha de inicio
            if self.availability_start_date <= now:
                self.is_published = True
            else:
                self.is_published = False
        elif self.availability_end_date: #Solo fecha de fin
            if now <= self.availability_end_date:
                self.is_published = True
            else:
                self.is_published = False
        else:
            # Si no hay fechas, no cambiar el estado actual
            pass
