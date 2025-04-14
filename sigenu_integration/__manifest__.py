{
    'name': 'Integración SIGENU',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'summary': 'Sincroniza facultades como compañías desde SIGENU',
    'description': """
        Conexión con la API de SIGENU para crear/actualizar compañías.
    """,
    'author': 'Rey y Keila',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/fetch_faculties_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
}