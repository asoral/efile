{
    'name':'Emp Attedance',
    'version': '12.0',
    'category': 'HRMS',
    'author': 'Dexciss Technology,Sid',
    'description':"""     """ ,
    'website': 'https://github.com/OCA/account-payment',
    'license': 'AGPL-3',
    
   'depends': [ 'date_range', 'hr','hr_attendance','base','currated_attendance','resource','hr_holidays'],
    #hr_holidays because it uses color_name field from 	hr.leave.type
    'data': [
        'security/ir.model.access.csv',
        'wizard/emp_attendance_wizard_view.xml',
        'report/emp_attendance_report.xml',
        
        
    ],
    'demo': [
       
    ],
    'installable': True,
}
