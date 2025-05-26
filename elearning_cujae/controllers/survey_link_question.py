from odoo.addons.survey.controllers import main
from odoo import http
from odoo.http import request
import random
from random import shuffle

class SurveyLinkQuestion(main.Survey):

    def _prepare_question_html(self, survey_sudo, answer_sudo, **post):
        survey_data = super()._prepare_survey_data(survey_sudo, answer_sudo, **post)

        # 🔀 Agrega las respuestas desordenadas si la pregunta es de tipo 'link'
        question = survey_data.get('question')
        if question and question.question_type == 'link':
            # Solo usar respuestas si existen
            link_items = question.link_items.filtered(lambda i: i.answer)
            survey_data['shuffled_link_answers'] = random.sample(link_items, len(link_items))

        # Renderiza la parte del contenido
        if answer_sudo.state == 'done':
            survey_content = request.env['ir.qweb']._render('survey.survey_fill_form_done', survey_data)
        else:
            survey_content = request.env['ir.qweb']._render('survey.survey_fill_form_in_progress', survey_data)

        return {
            'survey_content': survey_content,
            'survey_navigation': request.env['ir.qweb']._render('survey.survey_navigation', survey_data),
            'background_image_url': survey_sudo.background_image_url,
        }