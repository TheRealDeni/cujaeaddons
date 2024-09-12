import werkzeug
import werkzeug.utils
import werkzeug.exceptions

from odoo import _
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.addons.website_slides_survey.controllers.slides import WebsiteSlidesSurvey
from odoo.addons.elearning_cujae.controllers.slides import WebsiteSlidesSurveyExam
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

    @http.route(['/slides/add_slide'], type='json', auth='user', methods=['POST'], website=True)
    def create_slide(self, *args, **post):
         if post['slide_category']=='certification':
            asd= WebsiteSlidesSurvey.create_slide(self,*args,**post)
            return asd
         elif post['slide_category']=='exam':            
            asd2 = WebsiteSlidesSurveyExam.create_slide(self,*args,**post)          
            return asd2
         elif post['slide_category']=='glossary':
            create_new_glossary = post['slide_category'] == "glossary" and not post['glossary']['id']
            linked_glossary_id = int(post.get('glossary', {}).get('id') or 0)
            if create_new_glossary:
                # If user cannot create a new glossary, no need to create the slide either.
                if not request.env['glossary.glossary'].check_access_rights('create', raise_exception=False):
                    return {'error': _('You are not allowed to create a glossary.')}

                # Create glossary first as glossary slide needs a glossary_id (constraint)
                post['glossary_id'] = request.env['glossary.glossary'].create({
                    'name': post['glossary']['name'],
                }).id
            elif linked_glossary_id:
                try:
                    request.env['glossary.glossary'].browse([linked_glossary_id]).read(['name'])
                except AccessError:
                    return {'error': _('You are not allowed to link a glossary.')}
                post['glossary_id'] = post['glossary']['id']
              #  post['survey_id']= post['glossary_id']
            result = super(WebsiteSlidesGlossary, self).create_slide(*args, **post)

            if post['slide_category'] == "glossary": 
                result['url'] = '/slides/slide/%s?fullscreen=1' % (slug(request.env['slide.slide'].browse(result['slide_id']))),
            return result
         else:
            result = super(WebsiteSlidesGlossary, self).create_slide(*args, **post)
            return result
        
   
    @http.route(['/slides_survey/glossary/search_read'], type='json', auth='user', methods=['POST'], website=True)
    def slides_glossary_search_read_glossary(self, fields):
        can_create = request.env['glossary.glossary'].check_access_rights('create', raise_exception=False)
        return {
            'read_results': request.env['glossary.glossary'].search_read([], fields),
            'can_create': can_create,
        }

    def _get_valid_slide_post_values(self):
        result = super(WebsiteSlidesGlossary, self)._get_valid_slide_post_values()
        result.append('glossary_id')
        return result
    def _slide_mark_completed(self, slide):
        if slide.slide_category == 'glossary':
            raise werkzeug.exceptions.Forbidden(_("exam slides are completed when the glossary is seen."))
        return super(WebsiteSlidesGlossary, self)._slide_mark_completed(slide)
    
    @http.route('/slide/complete_slide', type='json', auth='user')
    def complete_slide(self, slide_id):
        slide = http.request.env['slide.slide'].browse(slide_id)
        if slide:
            slide.user_membership_id.completed = True  # O cualquier lógica adicional que necesites
        return {'success': True}