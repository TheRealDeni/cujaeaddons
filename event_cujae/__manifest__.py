{
    'name': 'event_cujae',
    'author': "Marlon Gonzalez Baro",
    "category": "Tools",
    "depends": ['base', 'event', 'website_event', 'mail', 'web', "mass_mailing_event","website_event_track_live"],

    'data': [
        'security/event_cujae_groups.xml',
        'security/ir.model.access.csv',        'views/event_views.xml',
        'views/reviewer_views.xml',
        'views/scientific_work_views.xml',
        'views/submission_page.xml',
        'views/submission_confirmation.xml',
        'views/view_conference_speakers.xml',
        'views/scientific_url_views.xml',
        'data/faculty_data.xml',
        'data/responsible_data.xml',
        'data/event_type_data.xml',
        'data/event_stage_data.xml',
    ],
    'images':[
        'static/description/icon.png',
    ],
    'assets': {
    'web.assets_backend': [
        'event_cujae/static/src/js/event_stage_confirm.js',
    ],
    },
    'license': 'AGPL-3',
    "installable": True,
    'application': True,
}
