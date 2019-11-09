{
    'name': 'Currated Attendance',
    'version': '12.0.0.5',
    'category': 'Custom Module category description(dexciss)',
    'sequence': 50,
    'description': """
                Last updated by smehata Gupta 16/10/2019
                Last updated by Rishab Gupta 04/10/2019 in _compute_is_overtime method
                Last updated by SMehata 09/09/2019 in generate roster
                Last updated by Maithili 3/09/2019 in generate roster
                Last updated by priyanka & sid(22/08/2019) change buffer time caculations. 
                This module add the  Employee Roster and currated attendance functionality to Employee""",
    'author': "@Ragini/DJ",
    'website': "http://dexciss.com/",
    'depends': [
                'hr_attendance','web','resource','date_range','zkteco_biometric','hr_payroll'
               ],
    'data': [

            'data/process_attendance_cron.xml',
            'data/employee_weekoff_demo.xml',
            'security/ir.model.access.csv',
            # 'wizard/process_attendance_wizard_view.xml',
            # 'wizard/actual_break_info_wizard_view.xml',
            'views/hr_roster_views.xml',
            'views/currated_attendance_view.xml',
            'views/overtime_request_views.xml',
            'views/generate_roster_views.xml',
            'views/res_config_view.xml',
            'views/currated_attendance_summary.xml',
            'views/resource_calendar_menu_inh.xml',
            'wizard/process_attendance_wizard_view.xml',
            'wizard/actual_break_info_wizard_view.xml',
            'wizard/currated_attendance_report_wizard.xml',


            ],
    
    'installable': True,
    'application': True,

}
