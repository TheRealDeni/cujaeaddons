import werkzeug
import werkzeug.utils
import werkzeug.exceptions

from odoo import _
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression

class MyController(http.Controller):
    @http.route(route='/examen',website=True, type='http')
    def asd(self, **kw):
        return 'HOLAA'