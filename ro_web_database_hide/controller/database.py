# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.database import Database as Database
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class NewDataBase(Database):
    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        raise http.request.not_found()

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        raise http.request.not_found()

