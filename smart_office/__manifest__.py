# -*- coding: utf-8 -*-
{
    'name': "Smart Office",

    'summary': """
            Smart Office
             """,

    'description': """
        Smart Office
    """,

    'author': "Sachin Burnawal",
    'website': "https://theerpstore.com/",
    'category': 'Smart Office',
    'version': '0.1',

    'depends': ['mail', 'muk_dms', 'muk_dms_actions', ],

    'data': [
        'data/data.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'views/add_letter.xml',
        'views/letters_view.xml',
        'views/add_files.xml',
        'views/files_view.xml',
        'views/wizard.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
    ],
    # 'installable': True,
    'application': True,
}
