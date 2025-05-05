import requests
from requests.auth import HTTPBasicAuth
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class FetchFacultiesWizard(models.TransientModel):
    _name = 'fetch.faculties.wizard'
    _description = 'Fetch Faculties from SIGENU'

    def fetch_faculties(self):
        url = "https://sigenu.cujae.edu.cu/sigenu-rest/dss/getfaculty"
        username = self.env['ir.config_parameter'].sudo().get_param('sigenu_integration.sigenu_username')
        password = self.env['ir.config_parameter'].sudo().get_param('sigenu_integration.sigenu_password')
        
        _logger.info(f"Intentando conectar a {url} con usuario: {username}")
        
        try:
            # Configurar sesión con User-Agent y auth
            session = requests.Session()
            session.auth = (username, password)
            session.headers.update({"User-Agent": "Odoo/16.0"})
            
            response = session.get(url, timeout=10)  
            _logger.info(f"Respuesta recibida - Status: {response.status_code}")
            
            if response.status_code == 401:
                _logger.error("Credenciales inválidas o falta de autenticación")
                raise UserError(_("Error 401: Credenciales incorrectas o acceso no autorizado."))
            
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(_("Error al conectar con SIGENU: %s") % e)

        try:
            faculties = response.json()
        except ValueError:
            raise UserError(_("Respuesta inválida desde SIGENU"))

        # Procesar facultades
        country_cu = self.env.ref('base.cu')
        main_company = self.env.ref('base.main_company')
        for faculty in faculties:
            existing = self.env['res.company'].search([('faculty_id', '=', faculty['IdFacultad'])], limit=1)
            vals = {
                'name': faculty['nombre'],
                'phone': faculty.get('telf', ''),
                'dean_name': faculty.get('nombreDecano', ''),
                'secretary_name': faculty.get('nombreSecretario', ''),
                'faculty_id': faculty['IdFacultad'],
                'country_id': country_cu.id,
                'currency_id': main_company.currency_id.id,
            }
            if existing:
                existing.write(vals)
            else:
                self.env['res.company'].create(vals)

    def action_fetch_faculties(self):
        self.fetch_faculties()
        return {'type': 'ir.actions.act_window_close'}