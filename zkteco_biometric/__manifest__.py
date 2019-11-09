# -*- coding: utf-8 -*-
# Developer : Pavan Panchal
{
    'name': 'Zkteco Biometric',
    'author': 'Pavan Panchal',
    'version': '1.0.6',
    'summary': 'Biometric Attendance',
    'description': '''
                    change the menu row to raw by rishab (14/08/2019)
                   - Fix Row data duplication and cron job for the row data 
                   - Zkteco  and eSSL companies most of device supported
                   - Removed extra models
                 ''',
    'category': 'biometric',
    'depends': ['hr_attendance'],
    'data': [
            'security/ir.model.access.csv',
            'views/hr_employee.xml',
            'views/bio_server.xml',
            'views/visitor_log.xml',
            'views/row_attendance.xml',
            'views/ir_cron_bio_server.xml',
            'wizard/sh_message_wizard.xml',
    ],
    'installable': True,
}
