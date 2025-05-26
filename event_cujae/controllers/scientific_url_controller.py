from odoo import http
from odoo.http import request

class ScientificUrl(http.Controller):

    @http.route('/event/<model("event.event"):event>', type='http', auth='public', website=True)
    def scientific_url(self, event, **kw):
        # Renderiza tu template QWeb definido abajo
        return request.render('event_cujae.scientific_url_views',{
            'event': event
        })