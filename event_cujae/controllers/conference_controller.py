import base64

from odoo import http
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.tools import lazy

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
        else:
            values = self._prepare_event_register_values(event, **kw)  
            return request.render("website_event.event_description_full", values)     

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

   
    


    def _prepare_event_register_values(self, event, **post):
        """Return the require values to render the template."""
        urls = lazy(event._get_event_resource_urls)
        return {
            'event': event,
            'main_object': event,
            'range': range,
            'google_url': lazy(lambda: urls.get('google_url')),
            'iCal_url': lazy(lambda: urls.get('iCal_url')),
        }