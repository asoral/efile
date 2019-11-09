# -*- coding: utf-8 -*-
{
    'name': "Payment Advice Journals",

    'summary': """
            Payment Advice Journal Entry
             """,

    'description': """
        Payment Advice Journal Entry
    """,

    'author': "Sachin Burnawal",
    'website': "https://theerpstore.com/",
    'category': 'Payment Advice Journal Entry',
    'version': '0.1',

    'depends': ['l10n_in_hr_payroll', 'hr_payroll',],

    'data': [
        'views/hr_advice.xml',
        'views/report_payroll_advice_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    '# auto_install': True,
    'application': True,
}
