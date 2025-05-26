from odoo import fields, models, api,_
from odoo import exceptions
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import is_html_empty

class Channel(models.Model):
    _inherit = 'slide.channel'

    nbr_exam = fields.Integer("Number of exams", compute='_compute_slides_statistics', store=True)
    availability_start_date = fields.Datetime(string="Availability Start Date", default=fields.Datetime.now)
    availability_end_date = fields.Datetime(string="Availability End Date")
    user_ids = fields.Many2many('res.users', string='Responsibles', default=lambda self: [(4, self.env.user.id)])
    manual_override = fields.Boolean(
        string="Publicación Manual",
        help="Si está activo, el estado de publicación no se actualizará automáticamente basado en fechas.",
        default=False
    )

    @api.model
    def _cron_check_course_availability(self):
        """ Verificación de disponibilidad respetando sobreescritura manual """
        now = datetime.now()
        courses = self.search([])
        for course in courses:
            if course.manual_override:  # Ignorar cursos con sobreescritura manual
                continue
                
            new_status = course.is_published
            if course.availability_start_date and course.availability_end_date:
                new_status = course.availability_start_date <= now <= course.availability_end_date
            elif course.availability_start_date:
                new_status = now >= course.availability_start_date
            elif course.availability_end_date:
                new_status = now <= course.availability_end_date

            if course.is_published != new_status:
                course.with_context(auto_publish_update=True).write({'is_published': new_status})

    @api.constrains('availability_start_date', 'availability_end_date')
    def _check_availability_dates(self):
        for record in self:
            if record.availability_start_date and record.availability_end_date and record.availability_start_date > record.availability_end_date:
                raise UserError("La fecha de inicio de disponibilidad no puede ser posterior a la fecha de fin.")

    @api.onchange('availability_start_date', 'availability_end_date')
    def _onchange_availability_dates(self):
        if self.manual_override:
            return  # No hacer cambios si hay sobreescritura manual
            
        now = datetime.now()
        if self.availability_start_date and self.availability_end_date:
            self.is_published = self.availability_start_date <= now <= self.availability_end_date
        elif self.availability_start_date:
            self.is_published = now >= self.availability_start_date
        elif self.availability_end_date:
            self.is_published = now <= self.availability_end_date

    # Campos computados y métodos de permisos
    @api.depends('upload_group_ids', 'user_ids')
    @api.depends_context('uid')
    def _compute_can_upload(self):
        for record in self:
            if self.env.user in record.user_ids or self.env.is_superuser():
                record.can_upload = True
            elif record.upload_group_ids:
                record.can_upload = bool(record.upload_group_ids & self.env.user.groups_id)
            else:
                record.can_upload = self.env.user.has_group('website_slides.group_website_slides_manager')
                record.can_upload = self.env.user.has_group('website_slides.group_website_slides_officer')
        super(Channel,self)._compute_can_upload()

    @api.depends('channel_type', 'user_ids', 'can_upload')
    @api.depends_context('uid')
    def _compute_can_publish(self):
        for record in self:
            if not record.can_upload:
                record.can_publish = False
            elif self.env.user in record.user_ids or self.env.is_superuser():
                record.can_publish = True
            else:
                record.can_publish = self.env.user.has_group('website_slides.group_website_slides_manager')
                record.can_upload = self.env.user.has_group('website_slides.group_website_slides_officer')
        super(Channel,self)._compute_can_publish()

    @api.model_create_multi
    def create(self, vals_list):
        
        try:  
            for vals in vals_list:
                if not vals.get('channel_partner_ids') and not self.env.is_superuser():
                    vals['channel_partner_ids'] = [(0, 0, {'partner_id': self.env.user.partner_id.id})]
                if not is_html_empty(vals.get('description')) and is_html_empty(vals.get('description_short')):
                    vals['description_short'] = vals['description']
                vals['user_ids'] = [(4, self.env.user.id)]

            channels = super(Channel, self.with_context(mail_create_nosubscribe=True)).create(vals_list)

            for channel in channels:
                if channel.user_ids:
                    partners = channel.user_ids.mapped('partner_id')
                    channel._action_add_members(partners)
                if channel.enroll_group_ids:
                    channel._add_groups_members()

            return channels
        except exceptions.ValidationError as e:
            print("Error de validación: %s", e)
            raise
        except exceptions.UserError as e:
            print("Error de usuario: %s", e)
            raise
        except Exception as e:
            print("Error inesperado: %s", e)
            raise

    def write(self, vals):
        # Resetear sobreescritura manual si cambian las fechas
        if 'availability_start_date' in vals or 'availability_end_date' in vals:
            vals['manual_override'] = False
            
        # Activar sobreescritura manual si se cambia manualmente is_published
        if 'is_published' in vals and not self.env.context.get('auto_publish_update'):
            vals['manual_override'] = True

        if 'description' in vals and not is_html_empty(vals['description']) and self.description == self.description_short:
            vals['description_short'] = vals['description']

        res = super().write(vals)

        if 'user_ids' in vals:
            new_users = self.user_ids - self._origin.user_ids
            partners = new_users.mapped('partner_id')
            self._action_add_members(partners)
            
            for user in self.user_ids:
                self.activity_reschedule(
                    ['website_slides.mail_activity_data_access_request'], 
                    new_user_id=user.id
                )

        if 'enroll_group_ids' in vals:
            self._add_groups_members()

        return res

    # Resto de métodos sin cambios
    def action_grant_access(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id).exists()
        if partner and self._action_add_members(partner):
            activities = self.activity_search(
                ['website_slides.mail_activity_data_access_request'],
                additional_domain=[
                    ('request_partner_id', '=', partner.id),
                    ('user_id', 'in', self.user_ids.ids)
                ]
            )
            activities.action_feedback(feedback=_('Access Granted'))

    def action_refuse_access(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id).exists()
        if partner:
            activities = self.activity_search(
                ['website_slides.mail_activity_data_access_request'],
                additional_domain=[
                    ('request_partner_id', '=', partner.id),
                    ('user_id', 'in', self.user_ids.ids)
                ]
            )
            activities.action_feedback(feedback=_('Access Refused'))

    def _action_request_access(self, partner):
        activities = self.env['mail.activity']
        requested_cids = self.sudo().activity_search(
            ['website_slides.mail_activity_data_access_request'],
            additional_domain=[('request_partner_id', '=', partner.id)]
        ).mapped('res_id')
        
        for channel in self:
            if channel.id not in requested_cids and channel.user_ids:
                for user in channel.user_ids:
                    activities += channel.activity_schedule(
                        'website_slides.mail_activity_data_access_request',
                        note=_('<b>%s</b> is requesting access to this course. Responsible: %s') % (
                            partner.name, 
                            ", ".join(channel.user_ids.mapped('name'))
                        ),
                        user_id=user.id,
                        request_partner_id=partner.id
                    )
        return activities

class ChannelUsersRelation(models.Model):
        _inherit = 'slide.channel.partner'

        channel_user_ids = fields.Many2many('res.users', string='Responsibles', related='channel_id.user_ids')
