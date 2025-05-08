from odoo import models, fields
from odoo.exceptions import UserError

class Glossary(models.Model):
    _name = 'glossary.glossary'
    _description = 'Glossary'
    _order = 'name asc'

    name = fields.Char(string='Nombre', required=True, translate=True)
    description = fields.Text(string='Descripción', translate=True)
    term_ids = fields.One2many('glossary.term', 'glossary_id', string='Términos')

    