{
    'name': 'Cujae Custom',
    'version': '1.0',
    'depends': ['base','website'],
    'category': 'Website/Theme',
    'author': 'Reinaldo Balmaseda y Keila Brunet',
    'data': [
        'views/assets.xml',
    ],
    'web._assets_primary_variables': [
      ('prepend', 'website_airproof/static/src/scss/primary_variables.scss'),
   ],
    'installable': True,
    'application': False,

}
