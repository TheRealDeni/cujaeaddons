from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class TravelForm(models.Model):
    _name = 'travel.form'
    _description = "Formulario de solicitud de viaje"

    #datos personales
    traveler_name = fields.Char(string="Nombre y apellidos", required=True)  # esto tiene que salir de los usuarios del sistema
    id_number = fields.Char(string="Carnet de identidad",
                            required=True)  # esto tiene que salir de los usuarios del sistema
    gender = fields.Selection(
        selection=[("male", "Masculino"), ("female", "Femenino")], required=True,
        string="Sexo")  # esto tiene que salir de los usuarios del sistema
    personal_address = fields.Char(string="Dirección particular",
                                   required=True)  # esto tiene que salir de los usuarios del sistema
    personal_email = fields.Char(string="Correo electrónico personal",
                                 required=True)  # esto tiene que salir de los usuarios del sistema
    work_email = fields.Char(string="Correo electrónico institucional",
                             required=True)  # esto tiene que salir de los usuarios del sistema
    personal_telephone_number = fields.Char(string="Teléfono personal",
                                            required=True)  # esto tiene que salir de los usuarios del sistema
    civil_status = fields.Selection(
        selection=[("married","Casado"),("single","Soltero"),("divorced","Divorciado"),("widow","Viudo")],
        required=True,
        string="Estado Civil"
    )  # esto tiene que salir de los usuarios del sistema
    has_child = fields.Boolean(string="Tiene hijos", required=True)  # esto tiene que salir de los usuarios del sistema
    children_situation = fields.Char(
        string="Persona que se encargará de cuidar a los hijos")  # hay que poner un required condicional

    #datos del viaje
    country = fields.Many2one("res.country", string="País de destino")
    applicant_type = fields.Char(string="Tipo de solicitante", required=True)  # cambiar a tipo selection
    applicant_area = fields.Selection(
        selection=[("cemat", "CEMAT"), ("ceis", "CEIS"), ("citi", "CITI")], required=True,
        string="Área a la que peretenece")  # esto tiene que salir de los usuarios del sistema
    travel_reason = fields.Char(string="Motivo del viaje", required=True)
    travel_concept = fields.Selection(
        selection=[("guest_teacher","Profesor invitado"),("academic_exchange","Intercambio académico"),
                   ("scholarship","Beca"),("event","Evento"),("international_degree","Postgrado internacional"),
                   ("commercial_mission","Misión Comercial"),("technical_advisory","Asesoría técnica"),
                   ("international_project","Proyecto internacional"),("chancellor_meeting","Reunión de rectores"),
                   ("alba_mission","Misión del ALBA")], required=True, string="Concepto del viaje"
    )
    sponsor = fields.Char(string="Encargado de cubrir los gastos", required=True)
    sub_teacher = fields.Char(string="Sustituto en la docencia", required=True)
    sub_researcher = fields.Char(string="Sustituto en la investigación", required=True)
    rank_n_subs = fields.Char(string="Cargos y sustitutos")
    records = fields.Char(string="Antecedentes")#esto es many2one con este mismo modelo validando que sea el mismo viajero

    #préstamos
    loan_ids = fields.One2many('travel.loan', 'travel_id')

    #el objetivo de la estancia se ponen en el campo descripición, hay que hacerlo reuired para este proceso
    # si es militante pcc o ujc tiene que salir de los usuarios del sistema

    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string="Ticket asociado",
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        travel_forms = super().create(vals_list)

        for form in travel_forms:
            # Generar una descripción básica con datos del formulario
            description = f"""
                    <p><strong>Solicitud de viaje creada automáticamente</strong></p>
                    <ul>
                        <li><b>Viajero:</b> {form.traveler_name or 'N/A'}</li>
                        <li><b>Motivo:</b> {form.travel_reason or 'N/A'}</li>
                        <li><b>País:</b> {form.country.name or 'N/A'}</li>
                        <li><b>Área:</b> {form.applicant_area or 'N/A'}</li>
                    </ul>
                    <p>Este ticket fue generado desde el formulario de viaje.</p>
                """
            # Obtener el ID del equipo "Grupo de Trámites Migratorios" (usando su XML ID)
            team_id = self.env.ref('gtm_cujae.team_grupo_tramites_migratorios').id
            type_id = self.env.ref('gtm_cujae.type_tramites_migratorios').id  # Tipo "Solicitud de viaje al exterior"
            category_id = self.env.ref('gtm_cujae.category_viaje_exterior').id

            # Crear el ticket con solo los campos obligatorios + travel_form_id
            ticket = self.env['helpdesk.ticket'].create({
                'name': f"Solicitud de viaje - {form.traveler_name or 'Nuevo'}",
                'description': description,  # Campo requerido
                'travel_form_id': form.id,  # Asignar el formulario al ticket
                'team_id': team_id,  # Asignación fija al equipo gtm
                'type_id': type_id,  # Tipo fijo para trámites migratorios
                'category_id': category_id,  # Categoría fija para viajes
                # (El resto de campos se dejan con valores por defecto)
            })

            form.ticket_id = ticket.id  # Opcional: Guardar referencia inversa

        return travel_forms
