# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Channel(models.Model):
    _inherit = 'slide.channel'

    current_req_slide = fields.Many2one('slide.slide', compute='_get_current_required_slide')

    @api.depends('slide_ids.sequence', 'slide_ids.is_required')
    @api.depends_context('uid')
    def _get_current_required_slide(self):
        for channel in self:
            required_slides = channel.slide_ids.filtered('is_required')
            required_slides_learned = self.env['slide.slide.partner'].sudo().search([('slide_id', 'in', required_slides.ids),
                                                                                     ('partner_id', '=', self.env.user.partner_id.id),
                                                                                     ('completed', '=', True)])
            required_slides_not_learned = required_slides - required_slides_learned.mapped('slide_id')
            channel.current_req_slide = required_slides_not_learned[0] if required_slides_not_learned else False


class Slide(models.Model):
    _inherit = 'slide.slide'

    is_required = fields.Boolean('Required', default=False)
    missing_requirement = fields.Boolean('Missing requirement', compute='_get_missing_requirement')

    @api.depends('sequence', 'channel_id.current_req_slide')
    @api.depends_context('uid')
    def _get_missing_requirement(self):
        for slide in self:
            req_slide = slide.channel_id.current_req_slide
            slide.missing_requirement = req_slide and not slide.is_preview and slide.sequence > req_slide.sequence


class SlidePartner(models.Model):
    _inherit = 'slide.slide.partner'

    @api.constrains('slide_id', 'partner_id')
    def required_slide_constrain(self):
        for record in self:
            slide = record.slide_id
            if slide.missing_requirement:
                raise UserError(_("You need to learn required slide first."))
