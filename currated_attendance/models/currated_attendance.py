from odoo import fields, models, api, _
from datetime import datetime, timedelta,time
from odoo.tools import float_round
import math


def convert_datestring_into_datetime(sting_date):
    datetime_value = datetime.strptime(sting_date, '%Y-%m-%d %H:%M:%S')
    return datetime_value


#Added Weekoff in Weekdays
class EmployeeWeekoffs(models.Model):
    _name = 'employee.weekoff'
    _description = "Employee Weekoff"
    _rec_name = "name"

    name = fields.Char(string="Week Day")
    code = fields.Integer(string="Week code")


class Employees(models.Model):
    _inherit = 'hr.employee'
    _description = "Employee"

    weekoff_ids = fields.Many2many('employee.weekoff',string="Weekly Offs")


class CuratedAttendance(models.Model):
    _name='currated.attendance'
    _description = "Curated Attendance"

    employee_id=fields.Many2one('hr.employee', string='Employee ID')
    check_in=fields.Datetime(string='Check-In')
    check_out = fields.Datetime(string='Check-Out')
    department_id = fields.Many2one('hr.department', string='Department')

    # operating_unit_id = fields.Many2one('operating.unit', string="Operating Unit")
    roster_id=fields.Many2one('hr.attendance.roster', string="Roster")

    expected_start=fields.Datetime(string='Expected Start')
    expected_end = fields.Datetime(string='Expected End')

    duty_hours = fields.Float(string='Duty Hours', compute="_compute_duty_hour" ,store=True)
    expected_duty_hours = fields.Float(string='Expected Duty Hours', compute="_compute_expected_duty_hours",store=True)
    expected_break = fields.Datetime(string='Expected Break')
    actual_break = fields.Datetime(string='Actual Break')
    early_going = fields.Boolean(string="Early Going",default=False, compute="_compute_early_going",store=True)#,compute="onchange_checkin_checkout_values"
    early_going_min = fields.Float(string="Early Going Minutes", compute="_compute_early_going_min",store=True)
    late_coming = fields.Boolean(string="Late Coming",default=False, compute="_compute_late_coming",store=True)
    late_coming_min = fields.Float(string="LateComing Minutes", compute="_compute_late_coming_min",store=True)
    absent = fields.Boolean(string="Absent",default=False, compute="_compute_is_absent",store=True)
    overtime = fields.Boolean(string="Overtime",default=False, compute="_compute_is_overtime",store=True)
    overtime_hours = fields.Float(string="Overtime Time",compute="_compute_is_overtime",store=True)
    lc_and_eg = fields.Boolean(string="LC and EG",default=False)
    exception = fields.Boolean(string="Exception",default=False, compute="_compute_is_exception",store=True)

    threshold_late = fields.Boolean(string='Late Threshold',compute="_compute_threshold_late_coming_minute",store=True)
    threshold_late_minute = fields.Float(string='Late Threshold Minute',compute="_compute_late_threshold_min",store=True)
    company_id = fields.Many2one('res.company', string='Company' )
    user_id = fields.Many2one('res.users', string='User')
    
    half_hr_ded = fields.Boolean(string="Half Hour Deduction",compute="_compute_deductions",default=False,store=True)
    half_day_ded = fields.Boolean(string="Half Day Deduction",compute="_compute_deductions",default=False,store=True)
    
    
    def value_to_html(self, value):
        sign = math.copysign(1.0, value)
        hours, minutes = divmod(abs(value) * 60, 60)
        minutes = round(minutes)
        if minutes == 60:
            minutes = 0
            hours += 1
        return '%02d.%02d' % (sign * hours, minutes)
    

    
    @api.depends('late_coming_min')
    def _compute_deductions(self):
        for s in self:
            if s.late_coming_min:
                late_min = float(s.value_to_html(s.late_coming_min))
                
                if late_min > 10.59  and late_min <= 30.00:
                    s.half_hr_ded = True
                elif late_min > 30.00:
                    s.half_day_ded = True
                
    @api.depends('roster_id', 'late_coming_min')
    def _compute_late_threshold_min(self):
        # print("-------------_compute_late_threshold_min--------------")
        for s in self:
            if s.roster_id and s.late_coming_min:
                buffer= s.roster_id.shift_id.buffer_time_float
                late_minute = s.late_coming_min
                # print("-------buffer----------late_minute---------------------",buffer,late_minute)
                late_min = late_minute - buffer
                # print("------late_min-------",late_min)
                if late_min > 0.00:
                    s.threshold_late_minute = late_min


    @api.depends('threshold_late_minute')
    def _compute_threshold_late_coming_minute(self):
        # print("-----------_compute_threshold_late_coming_minute------------")
        for s in self:
            if s.threshold_late_minute:
                s.threshold_late = True
            else:
                s.threshold_late = False

    @api.depends('check_in', 'check_out')
    def _compute_duty_hour(self):
        for s in self:
            if s.check_in and s.check_out:
                check_in = s.check_in
                check_out = s.check_out
                if check_in.year == check_out.year and check_in.month == check_out.month and check_in.day == check_out.day:
                    c = check_out - check_in
                    s.duty_hours = float_round(
                        float((float(c.seconds) / 60.0) / 60.0), 2)

    @api.depends('expected_start', 'expected_end')
    def _compute_expected_duty_hours(self):
        for s in self:
            if s.expected_start and s.expected_end:
                expected_start = s.expected_start 
                expected_end = s.expected_end 
                if expected_start.year == expected_end.year and expected_start.month == expected_end.month and expected_start.day == expected_end.day:
                    c = expected_end - expected_start
                    s.expected_duty_hours = float_round(
                        float((float(c.seconds) / 60.0) / 60.0), 2)

    @api.depends('check_out', 'expected_end')
    def _compute_early_going_min(self):
        for s in self:
            if s.expected_end and s.check_out:
                check_out =  s.check_out 
                expected_end = s.expected_end 
                c = expected_end - check_out 
                if c.days > 0:
                    s.early_going_min = float((float(c.seconds) /60))
                else:
                    s.early_going_min = 0.0

    @api.depends('early_going_min')
    def _compute_early_going(self):
        for s in self:
            if s.early_going_min:
                s.early_going = True
            else:
                s.early_going = False

    @api.depends('check_in', 'expected_start')
    def _compute_late_coming_min(self):
        for s in self:
            if s.expected_start and s.check_in:
                check_in =s.check_in 
                expected_start = s.expected_start 
                c = check_in - expected_start
                # print("------------_compute_late_coming_min------------------------------------",c,c.seconds)
                if c.days >= 0:
                    # s.late_coming_min = float((float(c.seconds) / 60.0) / 60.0)
                    s.late_coming_min = float((float(c.seconds) /60))
                else:
                    s.late_coming_min = 0.0

    @api.depends('late_coming_min')
    def _compute_late_coming(self):
        for s in self:
            if s.late_coming_min:
                s.late_coming = True
            else:
                s.late_coming = False

    @api.depends('check_in', 'check_out')
    def _compute_is_absent(self):
        for s in self:
            if not s.check_in and not s.check_out:
                s.absent = True
            else:
                s.absent = False

    @api.depends('check_in', 'check_out')
    def _compute_is_exception(self):
        for s in self:
            if not s.check_in or not s.check_out:
                s.exception = True
            else:
                s.exception = False

    @api.depends('duty_hours', 'expected_duty_hours','check_out','expected_end')
    def _compute_is_overtime(self):
        for s in self:
            if s.check_out and s.expected_end:
                time = s.check_out - s.expected_end
                if time.seconds >= 3600:
                    s.overtime = True
                    minutes = time.total_seconds() // 60
                    hours = minutes // 60
                    s.overtime_hours = float("%02d.%02d" % (hours, minutes % 60))
#                     s.overtime_hours = float(s.check_out - s.expected_end)
                else:
                    s.overtime = False


    @api.onchange('expected_start','expected_end')
    def _get_duty_hours(self):
        if self.expected_start and self.expected_end:
            data1 = self.expected_start
            data2 = self.expected_end
            diff = data2 - data1
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
        self.expected_duty_hours = hours


    @api.onchange('check_in', 'check_out')
    def _get_duty_hours(self):
        dhours = 0.0
        if self.expected_start and self.expected_end:
            data1 =self.check_in
            data2 = self.check_out 
            diff = data2 - data1
            days, seconds = diff.days, diff.seconds
            dhours = days * 24 + seconds // 3600
        self.duty_hours = dhours

    @api.multi
    def actual_break_button(self):
        context = dict(self.env.context or {})
        wizard_id = self.env['actual.break.information.wizard'].create({
            'currated_attendance_ref': self.id,
        })
        config_data = self.env['ir.config_parameter'].sudo().get_param(
            'currated_attendance.source_attendance_data_from')
        # print("-------------config_data-----------------------------------", config_data)

        if config_data == 'attendance':
            return {
                'name': 'Actual Break',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'actual.break.information.wizard',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('currated_attendance.actual_break_info_wizard_view').id,
                'nodestory': True,
                'target': 'new',
                'res_id': wizard_id.id,
                'context': context,
                }
        if config_data == 'raw_data':
            return {
                'name': 'Actual Break',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'actual.break.information.wizard',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('currated_attendance.row_attendance_info_wizard_view').id,
                'nodestory': True,
                'target': 'new',
                'res_id': wizard_id.id,
                'context': context,
            }





