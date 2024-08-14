# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Channel(models.Model):
    _inherit = 'slide.channel'

    nbr_exam = fields.Integer("Number of exams", compute='_compute_slides_statistics', store=True)
