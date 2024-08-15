# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.website_slides_survey.controllers.survey import Survey


class SurveyExam(Survey):
    def _prepare_survey_finished_values_ex(self, survey, answer, token=False):
        result = super(Survey, self)._prepare_survey_finished_values(survey, answer, token)
        if answer.slide_id:
            result['channel_id'] = answer.slide_id.channel_id

        return result

    def _prepare_retry_additional_values_ex(self, answer):
        result = super(Survey, self)._prepare_retry_additional_values(answer)
        if answer.slide_id:
            result['slide_id'] = answer.slide_id.id
        if answer.slide_partner_id:
            result['slide_partner_id'] = answer.slide_partner_id.id

        return result
