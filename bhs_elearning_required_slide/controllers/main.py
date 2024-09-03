# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from collections import defaultdict

import base64
import json
import logging
import math
import werkzeug

from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class WebsiteSlides(WebsiteProfile):

    @http.route('/slides/slide/toggle_is_required', type='json', auth='user', website=True)
    def toggle_slide_required(self, slide_id):
        slide = request.env['slide.slide'].browse(int(slide_id))
        if slide.channel_id.can_publish:
            slide.is_required = not slide.is_required
        return slide.is_required

    @http.route('/slides/slide/required_slide', type='json', auth='public', website=True)
    def get_required_slide(self, slide_id):
        slide = request.env['slide.slide'].sudo().browse(int(slide_id))
        channel_id = slide.channel_id
        required_slide = channel_id.current_req_slide if slide.sequence > channel_id.current_req_slide.sequence else False
        if not required_slide:
            return False

        return {'id': required_slide.id,
                'name': required_slide.name,
                'url': required_slide.website_url,
                'can_skip': slide.is_preview}


