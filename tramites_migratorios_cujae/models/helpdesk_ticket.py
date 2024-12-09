from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
