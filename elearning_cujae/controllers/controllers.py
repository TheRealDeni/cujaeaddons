# -*- coding: utf-8 -*-
# from odoo import http


# class Cxc(http.Controller):
#     @http.route('/cxc/cxc', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cxc/cxc/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cxc.listing', {
#             'root': '/cxc/cxc',
#             'objects': http.request.env['cxc.cxc'].search([]),
#         })

#     @http.route('/cxc/cxc/objects/<model("cxc.cxc"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cxc.object', {
#             'object': obj
#         })
