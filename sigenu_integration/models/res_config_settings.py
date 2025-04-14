from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sigenu_username = fields.Char(
        string="SIGENU Username",
        config_parameter='sigenu_integration.sigenu_username'
    )
    sigenu_password = fields.Char(
        string="SIGENU Password",
        config_parameter='sigenu_integration.sigenu_password',
        password=True
    )