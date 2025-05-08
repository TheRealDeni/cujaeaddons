from odoo import http
from odoo.http import request

class Conference(http.Controller):

    @http.route('/event/<model("event.event"):event>', type='http', auth='public', website=True)
    def conferencia_speakers(self, event, **kw):
        # Renderiza tu template QWeb definido abajo
        return request.render('event_cujae.view_conference_speakers',{
            'event': event
        })