import base64

from odoo import http
from odoo.http import request

class Conference(http.Controller):

    @http.route('/event/<model("event.event"):event>/register', type='http', auth='public', website=True)
    def override_register(self, event, **kw):
        # aquí puedes redirigir o renderizar tu propia plantilla
        if event.submission_page_url :
            return request.render('event_cujae.scientific_url_views', {'event': event})
        elif event.event_type_id.name == 'Conferencia':
            return request.render('event_cujae.view_conference_speakers', {'event': event})
        elif event.event_type_id.name == 'Científico':
            return request.redirect(f'event/submit_work/{event.id}')
        # si quieres seguir con el flujo normal
        return super(self).register(event, **kw)

    @http.route('/conferencia/<model("event.event"):event>', type='http', auth='public', website=True)
    def conference_speakers(self, event, **kw):
        return request.render('event_cujae.view_conference_speakers', {'event': event})

    # GET para ver la URL científica
    @http.route('/cientifico/<model("event.event"):event>', type='http', auth='public', website=True)
    def scientific_url(self, event, **kw):
        return request.render('event_cujae.scientific_url_views', {'event': event})

    # GET del formulario de subida
    @http.route('/event/submit_work/<model("event.event"):event>', type='http', auth='public', website=True)
    def submit_work_form(self, event, **kw):
        return request.render('event_cujae.view_submission_page', {'event': event})

    # POST del formulario
    @http.route('/event/submit_work', type='http', auth='public', website=True, methods=['POST'])
    def submit_work(self, **post):
        # tu lógica de creación de scientific.work…
        return request.redirect('/event/submission_confirmation')