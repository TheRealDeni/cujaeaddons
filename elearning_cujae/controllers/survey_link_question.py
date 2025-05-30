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

        survey_progress = False
        if answer_sudo.state == 'in_progress' and not survey_data.get('question',
                                                                      request.env['survey.question']).is_page:
            if survey_sudo.questions_layout == 'page_per_section':
                page_ids = survey_sudo.page_ids.ids
                survey_progress = request.env['ir.qweb']._render('survey.survey_progression', {
                    'survey': survey_sudo,
                    'page_ids': page_ids,
                    'page_number': page_ids.index(survey_data['page'].id) + (
                        1 if survey_sudo.progression_mode == 'number' else 0)
                })
            elif survey_sudo.questions_layout == 'page_per_question':
                page_ids = (answer_sudo.predefined_question_ids.ids
                            if not answer_sudo.is_session_answer and survey_sudo.questions_selection == 'random'
                            else survey_sudo.question_ids.ids)
                survey_progress = request.env['ir.qweb']._render('survey.survey_progression', {
                    'survey': survey_sudo,
                    'page_ids': page_ids,
                    'page_number': page_ids.index(survey_data['question'].id)
                })

        background_image_url = survey_sudo.background_image_url
        if 'question' in survey_data:
            background_image_url = survey_data['question'].background_image_url
        elif 'page' in survey_data:
            background_image_url = survey_data['page'].background_image_url

        return {
            'survey_content': survey_content,
            'survey_progress': survey_progress,
            'survey_navigation': request.env['ir.qweb']._render('survey.survey_navigation', survey_data),
            'background_image_url': background_image_url
        }