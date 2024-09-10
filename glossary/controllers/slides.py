import werkzeug
import werkzeug.utils
import werkzeug.exceptions

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides
import werkzeug

class WebsiteSlidesGlossary(WebsiteSlides):           
    @http.route(route='/slide/get_glossary_url', type='json', auth='user', website=True)
    def slide_get_glossary_url(self, slide_id, **kw):
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            raise werkzeug.exceptions.NotFound()
        slide = fetch_res['slide']
        glossary = slide.glossary_id
        terms = [{'name': term.name, 'description': term.description} for term in glossary.term_ids]

        values = {
            'glossary': glossary,
            'terms': terms,
        }

        return values  # Retornar como JSON
    @http.route('/slide/complete_slide', type='json', auth='user')
    def complete_slide(self, slide_id):
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            raise werkzeug.exceptions.NotFound()
        slide = fetch_res['slide']
        if slide:
            slide.completed = True  # O cualquier lógica adicional que necesites
        return {'success': True}