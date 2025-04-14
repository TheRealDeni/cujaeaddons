# -*- coding: utf-8 -*-
# from odoo import http


# class SigenuIntegration(http.Controller):
#     @http.route('/sigenu_integration/sigenu_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sigenu_integration/sigenu_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sigenu_integration.listing', {
#             'root': '/sigenu_integration/sigenu_integration',
#             'objects': http.request.env['sigenu_integration.sigenu_integration'].search([]),
#         })

#     @http.route('/sigenu_integration/sigenu_integration/objects/<model("sigenu_integration.sigenu_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sigenu_integration.object', {
#             'object': obj
#         })
