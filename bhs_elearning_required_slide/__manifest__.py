# -*- encoding: utf-8 -*-
{
    'name': "Elearning Slide Requirement",
    'version': '1.0',
    'summary': 'Requirement on specific slide',
    'category': 'elearning',
    'description': """
        A product of Bac Ha Software allows to require user to learn specific slide 
        before able to learn next slides.
    """,
    "depends": ['website_slides', 'website_slides_survey'],
    'data': [
        'views/slides_templates.xml',
        'views/slide_slide_view.xml',
    ],
    'license': 'LGPL-3',
    # Author
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'bhs_elearning_required_slide/static/src/scss/required_slide.scss',
         #   'bhs_elearning_required_slide/static/src/js/slides_slide_toggle_is_required.js',
          #  'bhs_elearning_required_slide/static/src/js/slides_slide_prevent_learning.js',
        ]
    }
}
