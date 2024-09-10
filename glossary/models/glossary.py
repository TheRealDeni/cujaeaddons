from odoo import models, fields

class Glossary(models.Model):
    _name = 'glossary.glossary'
    _description = 'Glossary'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    term_ids = fields.One2many('glossary.term', 'glossary_id', string='Términos')
