# -*- coding: utf-8 -*-
{
    'name': "eLearning CUJAE",

    'summary': """
        Modulo elearning Cujae
        """,
    'sequence': 1,

    'description': """
        Este módulo es para impartir cursos digitales
    """,

    'author': "Reinaldo y Keila",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website/eLearning',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_slides','survey','website_slides_survey'],

    # always loaded
    'data': [        
        'views/survey_question.xml',
        'security/security.xml'
        
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/account_move_demo.xml',
    ],

    # 'assets': {
    # 'web.assets_tests': [
    #     'l10n_cu_cxc/static/tests/tours/my_tour.js',
    # ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
