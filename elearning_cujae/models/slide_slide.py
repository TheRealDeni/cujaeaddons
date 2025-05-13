from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'

    user_input_ids = fields.One2many('survey.user_input', 'slide_partner_id', 'Exam attempts')
    exam_scoring_success = fields.Boolean('Exam completed', compute='_compute_survey_scoring_success', store=True)
    compute_survey_completed=fields.Boolean(string="Completed",compute="_compute_completed",store=True,help="True if user at least completed one time the survey."
)
    @api.depends('partner_id', 'user_input_ids.scoring_success')
    def _compute_exam_scoring_success(self):
        succeeded_user_inputs = self.env['survey.user_input'].sudo().search([
            ('slide_partner_id', 'in', self.ids),
            ('scoring_success', '=', True)
        ])
        succeeded_slide_partners = succeeded_user_inputs.mapped('slide_partner_id')
        for record in self:
            record.exam_scoring_success = record in succeeded_slide_partners
                
    @api.depends('user_input_ids.state')
    def _compute_completed(self):
        for record in self:
            # Verificar si existe al menos un intento en estado 'done'
            record.compute_survey_completed = bool(
                self.env['survey.user_input'].sudo().search_count([
                    ('slide_partner_id', '=', record.id),
                    ('state', '=', 'done')
                ], limit=1)
            )

    def _compute_field_value(self, field):
        super()._compute_field_value(field)
        if field.name == 'survey_scoring_success':
            # Iterar sobre cada registro en self
            for record in self:
                if record.survey_scoring_success:
                    record.compute_survey_completed=True
                    record.slide_id.env.user.sudo().add_karma(record.slide_id.karma_for_completion)
            
class Slide(models.Model):
    _inherit = 'slide.slide'

    slide_category = fields.Selection(selection_add=[
        ('exam', 'Exam')
    ], ondelete={'exam': 'set default'})
    slide_type = fields.Selection(selection_add=[
        ('exam', 'Exam')
    ], ondelete={'exam': 'set null'})
    exam_id = fields.Many2one('survey.survey', 'Exam')
    nbr_exam = fields.Integer("Number of exams", compute='_compute_slides_statistics', store=True)
    is_preview = fields.Boolean(compute='_compute_is_preview', readonly=False, store=True)
    karma_for_completion = fields.Integer("Karma gained when completed", readonly=False, store=True)
    availability_start_date = fields.Datetime(string="Availability Start Date", default=fields.Datetime.now)
    availability_end_date = fields.Datetime(string="Availability End Date")
    is_ending_soon = fields.Boolean(
        string="Ending soon",
        compute='_compute_is_ending_soon',
        store=True,
        help="True if the content has 1 week or less of availability."
    )
    ending_soon_notification_sent = fields.Boolean(
        string="Notificación enviada",
        default=False,
        help="Indicates if the notification has been sent."
    )
    manual_override = fields.Boolean(
        string="Publicación Manual",
        help="Si está activo, el estado de publicación no se actualizará automáticamente basado en fechas.",
        default=False
    )

    def _send_ending_soon_email(self):
        """Envía correo a los participantes del slide que NO han completado el contenido."""
        template = self.env.ref('elearning_cujae.mail_notification_ending_soon', raise_if_not_found=False)
        if not template:
            raise UserError("Mail template not found.")
        
        for slide in self:
            slide_partners = self.env['slide.slide.partner'].search([
                ('slide_id', '=', slide.id),
                ('completed', '=', False),
                ('partner_id.email', '!=', False),
            ])
            partners = slide_partners.mapped('partner_id')

            for partner in partners:
                template.with_context(
                    partner_name=partner.name,
                    lang=partner.lang
                ).send_mail(slide.id, email_values={
                    'email_to': partner.email,
                    'recipient_ids': [(6, 0, [partner.id])]
                })
            
            slide.ending_soon_notification_sent = True

    def _get_is_ending_soon(self, end_date):
        """Helper function to determine if the end date is within a week."""
        if not end_date:
            return False
        now = fields.Datetime.now()
        time_diff = end_date - now
        return time_diff <= timedelta(days=7) and time_diff > timedelta(0)

    @api.depends('availability_end_date')
    def _compute_is_ending_soon(self):
        for slide in self:
            slide.is_ending_soon = self._get_is_ending_soon(slide.availability_end_date)

    @api.depends('exam_id', 'survey_id')
    def _compute_name(self):
        super(Slide, self)._compute_name()
        for slide in self:
            if not slide.name and slide.exam_id:
                slide.name = slide.exam_id.title

    def _compute_mark_complete_actions(self):
        slides_exam = self.filtered(lambda slide: slide.slide_category == 'exam')
        slides_exam.can_self_mark_uncompleted = False
        slides_exam.can_self_mark_completed = False
        super(Slide, self - slides_exam)._compute_mark_complete_actions()
            
    @api.model
    def _cron_update_ending_soon(self):
        now = fields.Datetime.now()
        slides = self.search([
            '|',
            ('availability_end_date', '>', now - timedelta(days=7)),
            ('availability_end_date', '<=', now + timedelta(days=8)),
        ])
        for slide in slides:
            new_value = self._get_is_ending_soon(slide.availability_end_date)
            if slide.is_ending_soon != new_value:
                slide.write({'is_ending_soon': new_value})

    @api.model
    def _cron_send_ending_soon_notifications(self):
        slides = self.search([('is_ending_soon', '=', True)])
        slides._send_ending_soon_email()

    @api.model
    def _cron_check_slide_availability(self):
        """Verificación de disponibilidad con sobreescritura manual"""
        today = datetime.now()
        slides = self.search([])
        for slide in slides:
            if slide.manual_override:  # Ignorar slides con sobreescritura manual
                continue
                
            new_status = slide.is_published
            if slide.availability_start_date and slide.availability_end_date:
                new_status = slide.availability_start_date <= today <= slide.availability_end_date
            elif slide.availability_start_date:
                new_status = today >= slide.availability_start_date
            elif slide.availability_end_date:
                new_status = today <= slide.availability_end_date

            if slide.is_published != new_status:
                slide.with_context(auto_publish_update=True).write({'is_published': new_status})

    @api.constrains('availability_start_date', 'availability_end_date')
    def _check_availability_dates(self):
        for record in self:
            if record.availability_start_date and record.availability_end_date and record.availability_start_date > record.availability_end_date:
                raise UserError("The availability start date cannot be after the availability end date.")

    @api.onchange('availability_start_date', 'availability_end_date')
    def _onchange_availability_dates(self):
        if self.manual_override:
            return  # No hacer cambios si hay sobreescritura manual
            
        today = datetime.now()
        if self.availability_start_date and self.availability_end_date:
            self.is_published = self.availability_start_date <= today <= self.availability_end_date
        elif self.availability_start_date:
            self.is_published = today >= self.availability_start_date
        elif self.availability_end_date:
            self.is_published = today <= self.availability_end_date

    @api.depends('slide_category')
    def _compute_is_preview(self):
        for slide in self:
            if slide.slide_category == 'exam' or not slide.is_preview:
                slide.is_preview = False

    @api.depends('slide_category', 'source_type')
    def _compute_slide_type(self):
        super(Slide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'exam':
                slide.slide_type = 'exam'

    @api.model_create_multi
    def create(self, vals_list):
        slides = super().create(vals_list)
        slides_with_survey = slides.filtered('exam_id')
        slides_with_survey.slide_category = 'exam'
        slides_with_survey._ensure_challenge_category()
        return slides

    def write(self, values):
        # Resetear sobreescritura manual si cambian las fechas
        if 'availability_start_date' in values or 'availability_end_date' in values:
            values['manual_override'] = False
            
        # Activar sobreescritura manual si se cambia manualmente is_published
        if 'is_published' in values and not self.env.context.get('auto_publish_update'):
            values['manual_override'] = True

        old_surveys = self.mapped('exam_id')
        result = super(Slide, self).write(values)
        
        if 'exam_id' in values:
            self._ensure_challenge_category(old_surveys=old_surveys - self.mapped('exam_id'))
        if 'availability_end_date' in values:
            values['ending_soon_notification_sent'] = False
        return result

    def unlink(self):
        old_surveys = self.mapped('exam_id')
        result = super(Slide, self).unlink()
        self._ensure_challenge_category(old_surveys=old_surveys, unlink=True)
        return result

    def _ensure_challenge_category(self, old_surveys=None, unlink=False):
        if old_surveys:
            old_exam_challenges = old_surveys.mapped('certification_badge_id').challenge_ids
            old_exam_challenges.write({'challenge_category': 'certification'})
        if not unlink:
            exam_challenges = self.survey_id.certification_badge_id.challenge_ids
            exam_challenges.write({'challenge_category': 'slides'})

    def _generate_exam_url(self, slide):        
        exam_urls = {}
        for slide in slide.filtered(lambda s: s.slide_category == 'exam' and s.exam_id or s.survey_id):
            if slide.channel_id.is_member:
                user_membership_id_sudo = slide.user_membership_id.sudo()
                if user_membership_id_sudo.user_input_ids:
                    last_user_input = next(user_input for user_input in user_membership_id_sudo.user_input_ids.sorted(
                        lambda user_input: user_input.create_date, reverse=True
                    ))
                    exam_urls[slide.id] = last_user_input.get_start_url()
                else:
                    user_input = slide.exam_id.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            'slide_id': slide.id,
                            'slide_partner_id': user_membership_id_sudo.id
                        },
                        invite_token=self.env['survey.user_input']._generate_invite_token()
                    )
                    exam_urls[slide.id] = user_input.get_start_url()
            else:
                user_input = slide.exam_id.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True, **{
                        'slide_id': slide.id
                    }
                )
                exam_urls[slide.id] = user_input.get_start_url()
        return exam_urls