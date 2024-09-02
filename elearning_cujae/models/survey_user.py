from odoo import fields, models, api
from odoo.osv import expression


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    slide_id = fields.Many2one('slide.slide', 'Related course slide',
        help="The related course slide when there is no membership information")
    slide_partner_id = fields.Many2one('slide.slide.partner', 'Subscriber information',
        help="Slide membership information for the logged in user",
        index='btree_not_null') # index useful for deletions in comodel
    
    slide_exam = fields.Boolean('Examen completado', compute='_compute_exam_input', store=True)



    @api.model_create_multi
    def create(self, vals_list):
        records = super(SurveyUserInput, self).create(vals_list)
        records._check_for_failed_attempt()
        return records

    def write(self, vals):
        res = super(SurveyUserInput, self).write(vals)
        if 'state' in vals:
            self._check_for_failed_attempt()
        return res

    def _compute_exam_input(self):
        if self.slide_id.exam_id.exam==True:
            self.slide_exam=True
            

    def _check_for_failed_attempt(self):
        """
        Si el usuario falla su último intento de certificación del curso,
        se les notifica por correo electrónico. 
        """

        if self:
            user_inputs = self.search([
                ('id', 'in', self.ids),
                ('state', '=', 'done'),
                ('scoring_success', '=', False),
                ('slide_partner_id', '!=', False)
            ])

            if user_inputs:
                for user_input in user_inputs:
                    if user_input.survey_id._has_attempts_left(user_input.partner_id, user_input.email, user_input.invite_token):
                        # skip if user still has attempts left
                        continue

                    self.env.ref('website_slides_survey.mail_template_user_input_certification_failed').send_mail(
                        user_input.id, email_layout_xmlid="mail.mail_notification_light"
                    )

                    # Código para expulsar al usuario del curso
                    if self.slide_id.slide_category=='certification' and self.slide_id.channel_id.enroll=='payment':
                        removed_memberships_per_partner = {}
                        removed_memberships = removed_memberships_per_partner.get(user_input.partner_id,self.env['slide.channel'])
                        removed_memberships |= user_input.slide_partner_id.channel_id
                        removed_memberships_per_partner[user_input.partner_id] = removed_memberships
                        for partner_id, removed_memberships in removed_memberships_per_partner.items():
                            removed_memberships._remove_membership(partner_id.ids)

                    # ¡Aquí añade la acción adicional que quieres realizar!
                    # Ejemplo: Registra un evento en el sistema de logs
                    