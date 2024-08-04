from odoo import models, fields, api

class Slide(models.Model):
    _inherit = 'slide.slide'

    name = fields.Char(compute='_compute_name', readonly=False, store=True)
    slide_category = fields.Selection(selection_add=[
        ('certification', 'Prueba mixta')
    ], ondelete={'certification': 'set default'})
    slide_type = fields.Selection(selection_add=[
        ('certification', 'Certification')
    ], ondelete={'certification': 'set null'})
    survey_id = fields.Many2one('survey.survey', 'Certification')
    nbr_certification = fields.Integer("Number of Certifications", compute='_compute_slides_statistics', store=True)
    # small override of 'is_preview' to uncheck it automatically for slides of type 'certification'
    is_preview = fields.Boolean(compute='_compute_is_preview', readonly=False, store=True)
