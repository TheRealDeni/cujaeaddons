
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

    organizer_faculty = fields.Many2one(
        'university.faculty',
        string='Facultad Organizadora',
        required=True,  # Campo requerido
        help='Seleccione la facultad organizadora del evento.'
    )
    responsible_faculty = fields.Many2one(
        'faculty.responsible',
        string="Responsable",
        required=True,  # Campo requerido
        help='Seleccione el responsable del evento.'
    )
    descripcion = fields.Text(
        string="Descripción",
        help="Proporcione una descripción detallada del evento."
    )
    event_type_name = fields.Char(
        string='Nombre del Tipo de Evento',
        compute='_compute_event_type_name',
        store=True,
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

        descripcion = self._clean_html(self.descripcion)
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


    def _create_submission_page(self):
        if self.submission_page_url:  # <--- Validación clave
            return

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        page = self.env['website.page'].create({
            'name': f'Subida de Trabajos - {self.name}',
            'url': f'/event/submit_work/{self.id}',
            'website_id': base_url.id,
            'view_id': self.env.ref('event_cujae.view_submission_page').id,
        })
        self.submission_page_url = f"{base_url}{page.url}"


    def _create_conference_page(self):
        """Crear página web con información de ponentes"""
        website = self.env['website'].get_current_website()
        self.env['website.page'].create({
            'name': f'Ponentes - {self.name}',
            'url': f'/conferencia/{self.id}',
            'website_id': website.id,
            'view_id': self.env.ref('event_cujae.view_conference_speakers').id,
        })

    def _create_scientific_url(self):
        """Crear página web con información de ponentes"""
        website = self.env['website'].get_current_website()
        self.env['website.page'].create({
            'name': f'URL - {self.name}',
            'url': f'/cientifico/{self.id}',
            'website_id': website.id,
            'view_id': self.env.ref('event_cujae.scientific_url_views').id,
        })