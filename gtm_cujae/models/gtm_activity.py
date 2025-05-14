# models/mail_activity.py
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def _get_restricted_users_domain(self):
        """
        Retorna dominio dinámico para filtrar usuarios según el tipo de actividad
        """
        pcc_group = self.env.ref('gtm_cujae.group_helpdesk_pcc')
        ujc_group = self.env.ref('gtm_cujae.group_helpdesk_ujc')

        # Obtenemos el tipo de actividad del contexto o del registro actual
        activity_type_id = self.env.context.get('default_activity_type_id') or self.activity_type_id.id

        if activity_type_id == self.env.ref('gtm_cujae.activity_type_pcc_validation').id:
            return [('groups_id', 'in', [pcc_group.id])]
        elif activity_type_id == self.env.ref('gtm_cujae.activity_type_ujc_validation').id:
            return [('groups_id', 'in', [ujc_group.id])]
        return []

    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        domain=_get_restricted_users_domain,
        index=True, required=True
    )

    @api.constrains('activity_type_id', 'user_id')
    def _check_user_validation_group(self):
        pcc_group = self.env.ref('gtm_cujae.group_helpdesk_pcc')
        ujc_group = self.env.ref('gtm_cujae.group_helpdesk_ujc')

        for activity in self:
            if activity.activity_type_id == self.env.ref('gtm_cujae.activity_type_pcc_validation'):
                if activity.user_id not in pcc_group.users:
                    raise ValidationError(_(
                        "Las actividades de Validación PCC solo pueden asignarse a usuarios del grupo Validador PCC. "
                        "El usuario %s no pertenece a este grupo.") % activity.user_id.name)

            elif activity.activity_type_id == self.env.ref('gtm_cujae.activity_type_ujc_validation'):
                if activity.user_id not in ujc_group.users:
                    raise ValidationError(_(
                        "Las actividades de Validación UJC solo pueden asignarse a usuarios del grupo Validador UJC. "
                        "El usuario %s no pertenece a este grupo.") % activity.user_id.name)