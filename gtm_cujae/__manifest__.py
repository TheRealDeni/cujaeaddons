{
    'name': "gtm_cujae",
    'author': "Ernesto",
    'website': "http://www.yourcompany.com",

    'summary': """
        Modulo Trámites Migratorios Cujae
        """,
    'sequence': 13,

    'description': """
        Este módulo es para gestionar los trámites migratorios de la CUJAE
    """,

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': [
        'base','helpdesk_mgmt','helpdesk_mgmt_project'
    ],

    'data':[
        'security/ir.model.access.csv',
        'data/gtm_data.xml',
        'views/gtm_menu.xml',
        'views/travel_request_views.xml',
        'views/travel_expense_views.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}