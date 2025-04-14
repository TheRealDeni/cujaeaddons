from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class TravelRequest(models.Model):
    _inherit = "helpdesk.ticket"
    _description = "Solicitud de viaje"

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
    work_email = fields.Char(string="Correo electrónico intitucional",
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
    country = fields.Many2one("res.country", string="Country")
    applicant_type = fields.Char(string="Tipo de solicitante", required=True)  # cambiar a tipo selection
    applicant_area = fields.Selection(
        selection=[("cemat", "CEMAT"), ("ceis", "CEIS"), ("citi", "CITI")], required=True,
        string="Área a la que peretenece")  # esto tiene que salir de los usuarios del sistema
    travel_reason = fields.Char(string="Motivo del viaje", required=True)
    travel_concept = fields.Selection(
        selection=[("guest_teacher","Profesor invitado"),("academic_exchange","Intercambio académico"),
                   ("scholarship","Beca"),("event","Evento"),("international_degree","Postgrado internacional"),
                   ("commertial_mission","Misión Comercial"),("technicla_advisory","Asesoría técnica"),
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


