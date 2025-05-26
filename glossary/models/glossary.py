from odoo import api, models, fields
from odoo.exceptions import UserError

class Glossary(models.Model):
    _name = 'glossary.glossary'
    _description = 'Glossary'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    term_ids = fields.One2many('glossary.term', 'glossary_id', string='Terms')