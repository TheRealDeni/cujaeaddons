{
    'name': 'Course Glossary',
    'version': '16.0.1.0.0',
    'summary': 'Add glossary content type to courses in Odoo Slides',
    'description': """
        This module allows you to add a new content type "Glossary" to courses in Odoo Slides.
        Users can create glossary terms related to the course, with descriptions, and have them ordered alphabetically.
    """,
    'category': 'Education',
    'author': 'Reinaldo y Keila',
    'website': 'https://yourwebsite.com',
    'depends': ['base','website_slides','elearning_cujae'],
    'data': [
        'security/ir.model.access.csv',
        'views/glossary_views.xml',
        'views/glossary_term_views.xml',
        'views/glossary_menu_views.xml',
        'views/slide_slide_views.xml',
        'views/website_slides_templates_lesson_fullscreen.xml',
        'views/website_slides_templates_lesson.xml',
        'views/website_slides_templates_utils.xml',

    ],
    'assets': {
        'web.assets_frontend': [
          'glossary/static/src/js/search_terms.js',
          'glossary/static/src/js/slides_course_fullscreen_player.js',
          'glossary/static/src/scss/glossary.scss',
          'glossary/static/src/xml/website_slides_fullscreen.xml',




     ],
    'installable': True,
    'application': True,
    'auto_install': False,
} }
