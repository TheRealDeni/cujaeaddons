from odoo import models, fields

class GlossaryTerm(models.Model):
    _name = 'glossary.term'
    _description = 'Glossary Term'

    name = fields.Char(string='Term', required=True)
    description = fields.Text(string='Descripción', required=True)
    glossary_id = fields.Many2one('glossary.glossary', string='Glosario de términos', ondelete='cascade')
