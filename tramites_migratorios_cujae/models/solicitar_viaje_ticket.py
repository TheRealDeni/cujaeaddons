from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class SolicitarViaje(models.Model):
    _inherit = "helpdesk.ticket"
nb