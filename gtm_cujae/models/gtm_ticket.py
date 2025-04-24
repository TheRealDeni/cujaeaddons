from odoo import api, fields, models

class Ticket(models.Model):
    _inherit = 'helpdesk.ticket'
    _description = "Modificaciones al helpdesk ticket"

    travel_expense_ids = fields.One2many(
        "travel.expense",
        "ticket_id",
        string="Costos del viaje"
    )

    travel_form_id = fields.Many2one(
        'travel.form',
        string="Formulario de Viaje"
    )


    traveler_name = fields.Char(related='travel_form_id.traveler_name', string="Nombre y apellidos", readonly=False)
    id_number = fields.Char(related='travel_form_id.id_number', string="Carnet de identidad", readonly=False)
    gender = fields.Selection(related='travel_form_id.gender', string="Sexo", readonly=False)
    personal_address = fields.Char(related='travel_form_id.personal_address', string="Dirección particular",
                                   readonly=False)
    personal_email = fields.Char(related='travel_form_id.personal_email', string="Correo electrónico personal",
                                 readonly=False)
    work_email = fields.Char(related='travel_form_id.work_email', string="Correo electrónico institucional",
                             readonly=False)
    personal_telephone_number = fields.Char(related='travel_form_id.personal_telephone_number',
                                            string="Teléfono personal", readonly=False)
    civil_status = fields.Selection(related='travel_form_id.civil_status', string="Estado Civil", readonly=False)
    has_child = fields.Boolean(related='travel_form_id.has_child', string="Tiene hijos", readonly=False)
    children_situation = fields.Char(related='travel_form_id.children_situation',
                                     string="Persona que se encargará de cuidar a los hijos", readonly=False)
    country = fields.Many2one(related='travel_form_id.country', string="Country", readonly=False)
    applicant_type = fields.Char(related='travel_form_id.applicant_type', string="Tipo de solicitante", readonly=False)
    applicant_area = fields.Selection(related='travel_form_id.applicant_area', string="Área a la que pertenece",
                                      readonly=False)
    travel_reason = fields.Char(related='travel_form_id.travel_reason', string="Motivo del viaje", readonly=False)
    travel_concept = fields.Selection(related='travel_form_id.travel_concept', string="Concepto del viaje",
                                      readonly=False)
    sponsor = fields.Char(related='travel_form_id.sponsor', string="Encargado de cubrir los gastos", readonly=False)
    sub_teacher = fields.Char(related='travel_form_id.sub_teacher', string="Sustituto en la docencia", readonly=False)
    sub_researcher = fields.Char(related='travel_form_id.sub_researcher', string="Sustituto en la investigación",
                                 readonly=False)
    rank_n_subs = fields.Char(related='travel_form_id.rank_n_subs', string="Cargos y sustitutos", readonly=False)
    records = fields.Char(related='travel_form_id.records', string="Antecedentes", readonly=False)
