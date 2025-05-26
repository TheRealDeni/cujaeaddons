from datetime import date
from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError
import unicodedata

class TravelForm(models.Model):
    _name = 'travel.form'
    _description = "Formulario de solicitud de viaje"

    name = fields.Char(string="Código", readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('travel.form'), copy=False)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    company_parent_id = fields.Many2one(related='company_id.partner_id', string='Company contact')
    traveler_name = fields.Many2one(
        'res.partner',
        string="Nombre y apellidos",
        required=True,
        ondelete='restrict',
        domain="[('is_company', '!=', True)]"
    )

    traveler_employee_reference = fields.Many2one(
        'hr.employee',string="Empleado asociado",
        domain="[('work_contact_id', '=', traveler_name)]",
        help="Se autocompleta al seleccionar el viajero",
        store=True
    )
    id_number = fields.Char(string="Carnet de identidad",  required=False)
    gender = fields.Selection(related="traveler_name.gender", string="Sexo", store=True)
    personal_address = fields.Char(related="traveler_name.address", string="Dirección particular", required=True)
    personal_email = fields.Char(related="traveler_name.email", string="Correo electrónico personal", store=True)
    work_email = fields.Char(string="Correo electrónico institucional", compute='_compute_work_email', store=True, required=False, default='')
    personal_telephone_number = fields.Char(related="traveler_name.mobile", string="Teléfono personal", store=True)
    applicant_type = fields.Selection(related="traveler_name.cujae_user_type", string="Tipo de solicitante", store=True)
    applicant_area = fields.Many2one('hr.department',related='traveler_employee_reference.department_id',
                                     string="Área a la que pertenece", domain="[]", store=True, readonly=False)
    job_position = fields.Many2one('hr.job', related='traveler_employee_reference.job_id',
                                   string="Categoría docente o plaza de trabajo", domain="[]", store=True, readonly=False)
    academic_level = fields.Selection(related='traveler_employee_reference.certificate',string="Nivel Escolar", store=True, readonly=False)

    #datos del viaje
    country = fields.Many2one("res.country", string="País de destino", required=True)
    departure_date = fields.Date(string="Fecha de Salida", required=True)
    return_date = fields.Date(string="Fecha de Regreso", required=True)
    foreign_institution = fields.Char(string="Institución")
    travel_concept = fields.Selection(
        selection=[("guest_teacher","Profesor invitado"),("academic_exchange","Intercambio académico"),
                   ("scholarship","Beca"),("event","Evento"),("international_degree","Postgrado internacional"),
                   ("commercial_mission","Misión Comercial"),("technical_advisory","Asesoría técnica"),
                   ("international_project","Proyecto internacional"),("chancellor_meeting","Reunión de rectores"),
                   ("alba_mission","Misión del ALBA")], required=True, string="Concepto del viaje"
    )
    sponsor = fields.Char(string="Encargado de cubrir los gastos", required=True)

    #información adicional
    travel_objective = fields.Html(string="Objetivos del viaje", required=True)
    sub_teacher = fields.Text(string="Sustituto en la docencia")
    sub_researcher = fields.Text(string="Sustituto en la investigación")
    rank_n_subs = fields.Text(string="Cargos que ocupa y sustitutos en cada uno")
    records = fields.Html(string="Antecedentes")
    invitation_letter = fields.Binary(
        string="Carta de invitación",
        attachment=True,
        required=False
    )

    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string="Ticket asociado",
        readonly=True,
        ondelete='restrict'
    )

    @api.onchange('traveler_name')
    def _onchange_traveler_name(self):
        if self.traveler_name:
            id_number = self.traveler_name.id_numbers.filtered(
                lambda r: r.category_id.code == 'c_id'
            )
            self.id_number = id_number[0].name if id_number else False
        else:
            self.id_number = False

    @api.model_create_multi
    def create(self, vals_list):
        travel_forms = super().create(vals_list)
        for form in travel_forms:
            description = f"""
                <p><strong>Solicitud de viaje creada automáticamente</strong></p>
                <ul>
                    <li><b>Viajero:</b> {form.traveler_name.name or 'N/A'}</li>
                    <li><b>Motivo:</b> {dict(form._fields['travel_concept'].selection).get(form.travel_concept) or 'N/A'}</li>
                    <li><b>País:</b> {form.country.name or 'N/A'}</li>
                    <li><b>Área:</b> {form.applicant_area.name or 'N/A'}</li>
                </ul>
                <p>Este ticket fue generado desde el formulario de viaje.</p>
            """

            team_id = self.env.ref('gtm_cujae.team_grupo_tramites_migratorios').id
            type_id = self.env.ref('gtm_cujae.type_tramites_migratorios').id
            category_id = self.env.ref('gtm_cujae.category_viaje_exterior').id
            ticket = self.env['helpdesk.ticket'].create({
                'name': f"Solicitud de viaje - {form.traveler_name.name or 'Nuevo'}",
                'description': description,
                'travel_form_id': form.id,  # Asignar el formulario al ticket
                'team_id': team_id,
                'type_id': type_id,
                'category_id': category_id,
                'partner_id': form.traveler_name.id,
                'partner_name': form.traveler_name.name,
            })
            form.ticket_id = ticket.id  #Guardar referencia inversa
        return travel_forms

    @api.constrains('departure_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.departure_date < date.today():
                raise ValidationError("La fecha de salida no puede ser anterior a la fecha actual.")
            if record.return_date < record.departure_date:
                raise ValidationError("La fecha de regreso no puede ser anterior a la fecha de salida.")

    @api.depends('traveler_name.name')
    def _compute_work_email(self):
        for record in self:
            if record.traveler_name and record.traveler_name.name:
                # Quitar tildes y caracteres especiales
                name = unicodedata.normalize('NFKD', record.traveler_name.name) \
                    .encode('ASCII', 'ignore') \
                    .decode('ASCII')
                # Convertir a minúsculas y eliminar espacios
                email_name = name.lower().replace(' ', '')
                # Eliminar caracteres extraños
                email_name = ''.join(c for c in email_name if c.isalnum())
                # Construir el email
                record.work_email = f"{email_name}@cujae.edu.cu"
            else:
                record.work_email = ''

    @api.constrains('traveler_name')
    def _check_traveler(self):
        for record in self:
            if not record.id_number:
                raise ValidationError("No se encontró número de identidad para el viajero seleccionado")

