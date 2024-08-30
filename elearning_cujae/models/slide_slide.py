from odoo import models, fields, api
class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'

    user_input_ids = fields.One2many('survey.user_input', 'slide_partner_id', 'Exam attempts')
    exam_scoring_success = fields.Boolean('Exam Succeeded', compute='_compute_survey_scoring_success', store=True)

    @api.depends('partner_id', 'user_input_ids.scoring_success')
    def _compute_exam_scoring_success(self):
        succeeded_user_inputs = self.env['survey.user_input'].sudo().search([
            ('slide_partner_id', 'in', self.ids),
            ('scoring_success', '=', True)
        ])
        succeeded_slide_partners = succeeded_user_inputs.mapped('slide_partner_id')
        for record in self:
            record.exam_scoring_success = record in succeeded_slide_partners

    def _compute_field_value(self, field):
        super()._compute_field_value(field)
        if field.name == 'exam_scoring_success':
            self.filtered('exam_scoring_success').write({
                'completed': True
            })
class Slide(models.Model):
    _inherit = 'slide.slide'

    name = fields.Char(compute='_compute_name', readonly=False, store=True)
    has_certification = fields.Boolean(string="Lleva certificación")
    certification = fields.Boolean(string="Es certificación?")
    slide_category = fields.Selection(selection_add=[
        ('exam', 'Exam')
    ], ondelete={'exam': 'set default'})
    slide_type = fields.Selection(selection_add=[
        ('exam', 'Exam')
    ], ondelete={'exam': 'set null'})
    exam_id = fields.Many2one('survey.survey', 'Examen')
    nbr_exam = fields.Integer("Number of exams", compute='_compute_slides_statistics', store=True)
    # small override of 'is_preview' to uncheck it automatically for slides of type 'exam'
    is_preview = fields.Boolean(compute='_compute_is_preview', readonly=False, store=True)

  

    @api.depends('exam_id')
    def _compute_name(self):
        for slide in self:
            if not slide.name and slide.exam_id:
                slide.name = slide.exam_id.title

    def _compute_mark_complete_actions(self):
        slides_exam = self.filtered(lambda slide: slide.slide_category == 'exam')
        slides_exam.can_self_mark_uncompleted = False
        slides_exam.can_self_mark_completed = False
        super(Slide, self - slides_exam)._compute_mark_complete_actions()

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
        old_surveys = self.mapped('exam_id')
        result = super(Slide, self).write(values)
        if 'exam_id' in values:
            self._ensure_challenge_category(old_surveys=old_surveys - self.mapped('exam_id'))
        return result

    def unlink(self):
        old_surveys = self.mapped('exam_id')
        result = super(Slide, self).unlink()
        self._ensure_challenge_category(old_surveys=old_surveys, unlink=True)
        return result

    def _ensure_challenge_category(self, old_surveys=None, unlink=False):
        """ If a slide is linked to a survey that gives a badge, the challenge category of this badge must be
        set to 'slides' in order to appear under the exam badge list on ranks_badges page.
        If the survey is unlinked from the slide, the challenge category must be reset to 'exam'"""
        if old_surveys:
            old_exam_challenges = old_surveys.mapped('certification_badge_id').challenge_ids
            old_exam_challenges.write({'challenge_category': 'certification'})
        if not unlink:
            exam_challenges = self.survey_id.certification_badge_id.challenge_ids
            exam_challenges.write({'challenge_category': 'slides'})

    def _generate_exam_url(self,slide):        
        exam_urls = {}
        print("generando url")
        print(slide.slide_category)
        print(slide.survey_id)
        print(slide.exam_id)

        if slide.survey_id == False:
             print("No hay un examen asociado a este slide")

        for slide in slide.filtered(lambda slide: slide.slide_category == 'exam' and slide.exam_id or slide.survey_id ):            
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