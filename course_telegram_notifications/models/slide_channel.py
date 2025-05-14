from odoo import models, fields, api, exceptions
import requests
import logging

from odoo.tools.convert import _

_logger = logging.getLogger(__name__)

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    telegram_bot_token = fields.Char(
        string="Bot Token",
        help="Token obtained from @BotFather. E.g.: '1234567890:ABCdefGhIJKLMNopqrstUVWXYZ'"
    )
    telegram_channel_id = fields.Char(
        string="Group/Channel ID",
        help="Group/channel ID is required the @ before the ID"
    )
    enable_telegram = fields.Boolean(string="Activate Telegram")



    def write(self, vals):
        if 'enable_telegram' in vals and not vals['enable_telegram']:
            vals.update({
                'telegram_bot_token': False,
                'telegram_channel_id': False,
            })
        return super().write(vals)
