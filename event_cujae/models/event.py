from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import requests
from html import unescape
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = 'event.event'

    name = fields.Char(
        string='Nombre del Evento',
        required=True,  # Campo requerido
        help='Proporcione el nombre del evento.'
    )
    date_begin = fields.Datetime(
        string='Fecha de Inicio',
        required=True,  # Campo requerido
        help='Proporcione la fecha de inicio del evento.'
    )

    description = fields.Text(
        string="Descripción",
        help="Proporcione una descripción detallada del evento."
    )
    event_type_name = fields.Char(
        string='Nombre del Tipo de Evento',
        related='event_type_id.name', store=True)

    is_published = fields.Boolean(
        string='Publicado en el sitio web',
        copy=False,
        default=False,
        help="Controla la visibilidad pública del evento"
    )

    speaker_ids = fields.Many2many('res.partner', string='Ponentes')
    submission_page_url = fields.Char(string='URL para subir trabajos')

    @api.depends('event_type_id.name')
    def _compute_event_type_name(self):
        for record in self:
            record.event_type_name = record.event_type_id.name

    @api.onchange('event_type_id')
    def _onchange_event_type_id(self):
        for record in self:
            if record.event_type_id.name == 'Conferencia':
                record.submission_page_url = False
            elif record.event_type_id.name == 'Científico':
                record.speaker_ids = [(6, 0, [])]

    @api.model
    def create(self, vals):
        event = super(Event, self).create(vals)
        # Manejar evento científico
        if event.submission_page_url:
            self._create_scientific_url()
        elif event.event_type_id.name == 'Científico' and not event.submission_page_url:
            self._create_submission_page()
        # Manejar evento de conferencia
        elif event.event_type_id.name == 'Conferencia':
            self._create_conference_page()
        # Publicar en Telegram
        event._post_to_telegram()
        return event

    def write(self, vals):

        old_stages = {ev.id: ev.stage_id.id for ev in self}
        res = super(Event, self).write(vals)

        if 'stage_id' in vals:

            published_stage_id = self.env['event.stage'].search([
                ('name', '=', 'Publicado'),
            ], order="sequence asc", limit=1).id
            canceled_stage_id = self.env['event.stage'].search([
                ('name', '=', 'Cancelado'),
            ], order="sequence asc", limit=1).id
            finished_stage_id = self.env['event.stage'].search([
                ('name', '=', 'Finalizado'),
            ], order="sequence asc", limit=1).id

            for ev in self:
                old_stage = old_stages.get(ev.id)
                new_stage = ev.stage_id.id

                if new_stage == published_stage_id:
                    ev.write({'website_published': True})  # Usamos el campo nativo de Odoo
                    _logger.info(f"Evento {ev.name} publicado en el sitio web")
                elif old_stage == published_stage_id and new_stage != published_stage_id:
                    ev.write({'website_published': False})

                # Notificar solo si NO venía de "Finalizado" y fue cambiado a "Cancelado"
                if old_stage != finished_stage_id and new_stage == canceled_stage_id:
                    ev._post_cancel_to_telegram()

        return res

    @staticmethod
    def _clean_html(html_content):
        if not html_content:
            return "Sin descripción"
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator="\n")
        return unescape(text.strip())

    def _post_to_telegram(self):
        """Publicar evento en Telegram"""
        telegram_bot_token = "7396987561:AAGMjZ-fvWcOFCtk_YILIWAxVLLWdumWHKY"
        telegram_chat_id = "@OdooEvent"

        descripcion = self._clean_html(self.description)
        message = (
            f'📢 ¡Nuevo evento publicado!\n\n'
            f'🎉 {self.name}\n'
            f'📅 Fecha: {self.date_begin.strftime("%d/%m/%Y %H:%M")}\n'
            f'📝 Descripción:\n{descripcion}'
        )

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                data={"chat_id": telegram_chat_id, "text": message, "parse_mode": "Markdown"}
            )
            if response.status_code != 200:
                _logger.error("Error en Telegram: %s", response.text)
        except requests.ConnectionError:
            _logger.warning("Falló la conexión a Telegram")

    def _post_cancel_to_telegram(self):
        """Publicar notificación de cancelación en Telegram"""
        telegram_bot_token = "7396987561:AAGMjZ-fvWcOFCtk_YILIWAxVLLWdumWHKY"
        telegram_chat_id = "@OdooEvent"

        # Construir mensaje
        message = (
            f'⚠️ <b>Evento Cancelado</b>\n\n'
            f'❌ {self.name}\n'
            f'📅 Fecha original: {self.date_begin.strftime("%d/%m/%Y %H:%M")}\n\n'
            f'Este evento ha sido cancelado. Disculpa las molestias.'
        )

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                data={
                    "chat_id": telegram_chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                }
            )
            if response.status_code != 200:
                _logger.error("Error en Telegram (cancelación): %s", response.text)
        except requests.ConnectionError:
            _logger.warning("Falló la conexión a Telegram al notificar la cancelación")

        for registration in self.registration_ids:
            partner = registration.partner_id
            if partner.email:
                mail_values = {
                    'subject': f'Cancelación del evento: {self.name}',
                    'body_html': f"""
                           <p>Estimado/a {partner.name},</p>
                           <p>Lamentamos informarle que el evento <strong>{self.name}</strong> programado para el día 
                           <strong>{self.date_begin.strftime('%d/%m/%Y %H:%M')}</strong> ha sido cancelado.</p>
                           <p>Disculpe las molestias ocasionadas.</p>
                           <p>Atentamente,<br/>Equipo organizador de eventos CUJAE</p>
                       """,
                    'email_to': partner.email,
                    'auto_delete': True,
                }
                self.env['mail.mail'].create(mail_values).send()

    def _create_submission_page(self):
        website = self.env['website'].get_current_website()
        self.env['website.page'].create({
            'name': 'Página de Envío de Trabajos',
            'url': f'/event/submit_work/{self.id}',
            'website_id': website.id,
        })

    def _create_conference_page(self):
        website = self.env['website'].get_current_website()
        self.env['website.page'].create({
            'name': f'Ponentes - {self.name}',
            'url': f'/conferencia/{self.id}',
            'website_id': website.id,
            'view_id': self.env.ref('event_cujae.view_conference_speakers').id,
        })

    def _create_scientific_url(self):
        website = self.env['website'].get_current_website()
        self.env['website.page'].create({
            'name': f'URL - {self.name}',
            'url': f'/cientifico/{self.id}',
            'website_id': website.id,
            'view_id': self.env.ref('event_cujae.scientific_url_views').id,
        })
