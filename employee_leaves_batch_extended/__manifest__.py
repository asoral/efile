
{
    'name': 'Employee LWP',
    'version': '1.0.0.0.4',
    'category':'HR',
    'author': 'Dexciss Technology Pvt Ltd (Sangita)',
    'license': 'AGPL-3',
    'summary': 'Employee LWP and Attendance',
    'description': """last Update sangita- 13/11/2018 add ver.(.1)
                    Last Update by sangita 2/03/2019 add Ver(.2)
                    Last Updated by Sangita 23/05/2019 added new LWP date fields ver.3""",
    'website': 'https://www.cubicerp.com',
    'depends': ['hr_payroll'],
    'data': [
        "view/emp_leave_without_pay_cal.xml",
    ],
    'qweb': [
    ],
    'demo': [],
    'test': [],
    'installable': True,
    '# auto_install': True,
    'application': True,
}
