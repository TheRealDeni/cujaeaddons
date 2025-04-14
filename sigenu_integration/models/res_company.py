from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    faculty_id = fields.Char(string="Faculty ID")
    dean_name = fields.Char(string="Dean Name")
    secretary_name = fields.Char(string="Secretary Name")