# models/glossary_inherit.py
from odoo import models, fields, api

class Slide(models.Model):
    _inherit = 'slide.slide'


    slide_category = fields.Selection(selection_add=[
        ('glossary', 'Glosario')
    ], ondelete={'glossary': 'set default'})
    slide_type = fields.Selection(selection_add=[
        ('glossary', 'Glosario')
    ], ondelete={'glossary': 'set null'})
    glossary_id = fields.Many2one('glossary.glossary', string='Glosario')
    nbr_glossary = fields.Integer("Número de glosarios", compute='_compute_slides_statistics', store=True)

    
    @api.depends('glossary_id')
    def _compute_name(self):
        super(Slide, self)._compute_name()
        for slide in self:
            if not slide.name and slide.glossary_id:
                slide.name = slide.glossary_id.name

    def _compute_mark_complete_actions(self):
        slides_glossary = self.filtered(lambda slide: slide.slide_category == 'glossary')
        slides_glossary.can_self_mark_uncompleted = False
        slides_glossary.can_self_mark_completed = False
        super(Slide, self - slides_glossary)._compute_mark_complete_actions()

    @api.depends('slide_category')
    def _compute_is_preview(self):
        super(Slide, self)._compute_is_preview()
        for slide in self:
            if slide.slide_category == 'glossary' or not slide.is_preview:
                slide.is_preview = False

    @api.depends('slide_category', 'source_type')
    def _compute_slide_type(self):
        super(Slide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'glossary':
                slide.slide_type = 'glossary'

