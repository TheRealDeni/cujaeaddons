from odoo import fields, models


class Channel(models.Model):
    _inherit = 'slide.channel'

    nbr_glossary = fields.Integer("Number of glossaries", compute='_compute_slides_statistics', store=True)
