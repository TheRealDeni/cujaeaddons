from odoo import api, models, fields

class GlossaryTerm(models.Model):
    _name = 'glossary.term'
    _description = 'Glossary Term'
    _order = 'name asc'

    name = fields.Char(string='Term', required=True, translate=True)
    description = fields.Html(string='Description', required=True, translate=True)  # Cambiado a HTML
    glossary_id = fields.Many2one('glossary.glossary', string='Glossary', ondelete='cascade')
    initial_letter = fields.Char(string='Inicial Letter', compute='_compute_initial_letter', store=True)
    
    @api.depends('name')
    def _compute_initial_letter(self):
        for term in self:
            if term.name:
                term.initial_letter = term.name[0].upper()
