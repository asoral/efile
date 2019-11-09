from odoo import fields, models, api, _

class CuratedAttendanceSummary(models.Model):
    _name='currated.attendance.summary'
    _description = "Curated Attendance Summary"

    employee_id = fields.Many2one('hr.employee', string='Employee ID')
    identification_id=fields.Char(string='Identification ID')
    work_location=fields.Char(string='Work Location')
    job_title=fields.Char(string='Job Title')
    job_id = fields.Many2one('hr.job',string='Job Position')
    grade_id=fields.Many2one('grade.grade',string='Grade')
    biometric_id = fields.Char(string='Bio Metric Id')
    department_id = fields.Many2one('hr.department', string='Department')
    expected_duty_hours = fields.Float(string='Expected Duty Hours')
    duty_hours = fields.Float(string='Duty Hours')
    working_days = fields.Float(string='Working Days')
    absent_days = fields.Float(string='Absent Days')
    worked_days = fields.Float(string='Present Days')
    no_of_late_coming = fields.Float(string='Number Of Late Coming')
    no_of_early_going = fields.Float(string='Number Of Early Going')
    late_comming_minute = fields.Float(string='Late Comming Minute')
    early_going_minute = fields.Float(string='Early Going Minute')
    over_time = fields.Float(string='Over Time')
    from_date=fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    threshold_late_count = fields.Float(string='Number Of Late Threshold')
    threshold_late_minute = fields.Float(string='Late Threshold Minute')
    company_id = fields.Many2one('res.company', string='Company')
    user_id = fields.Many2one('res.users', string='User')

    @api.multi
    def actual_attendacne_button(self):
        return {
            'name': 'Actual Attendance',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'currated.attendance',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('currated_attendance.currated_attendance_tree_view').id,
            'domain': [('employee_id', '=',self.employee_id.id),
                       ('expected_start', '>=', self.from_date),
                       ('expected_start', '<=', self.to_date),
                       ('expected_end', '<=', self.to_date),
                       ('expected_end', '>=', self.from_date)
                       ],
            'nodestory': True,
            'target': 'new',
        }