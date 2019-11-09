from odoo import fields, models, api, _
from datetime import datetime, timedelta



class actual_break_information(models.Model):
    _name = 'actual.break.information.wizard'
    _description = "Actual Break Information"

    currated_attendance_ref = fields.Many2one('currated.attendance',string="Attendance Ref")
    actual_break_line = fields.One2many('actual.break.information.line','actual_break_id')
    attendance_brk_lines = fields.Many2many('hr.attendance',string="Attendance Break Lines")
    actual_row_attendance = fields.One2many('actual.row.attendance.line','actual_row_id')

    @api.constrains('currated_attendance_ref')
    @api.onchange('currated_attendance_ref')
    def get_domain_for_attendances(self):
        config_data = self.env['ir.config_parameter'].sudo().get_param(
            'currated_attendance.source_attendance_data_from')
        # print("-------------config_data-----------------------------------", config_data)
        if config_data == 'attendance':
            attendance_ids = self.env['hr.attendance']
            if self.currated_attendance_ref:
                # print("we got curratrd attence===========>>>",self.currated_attendance_ref)
                if self.currated_attendance_ref.expected_start and self.currated_attendance_ref.expected_end:
                    yesterday = self.currated_attendance_ref.expected_start.date() - timedelta(days=1)
                    tommorrow = self.currated_attendance_ref.expected_start.date() + timedelta(days=1)
                    # print("===Yesterday========Tommorrow=",yesterday,tommorrow)
                    attendance_ids = self.env['hr.attendance'].search(
                        [('employee_id', '=', self.currated_attendance_ref.employee_id.id),('check_in', '>=', yesterday),
                         ('check_out', '<=', tommorrow)])
                    # print("attrn-------->>",attendance_ids,self.id,self._context)
                for attend in attendance_ids:
                    self.attendance_brk_lines += attend
                    self.env['actual.break.information.line'].create({
                        'actual_break_id': self.id,
                        'employee_id': self.currated_attendance_ref.employee_id.id,
                        'emp_in' : attend.check_in,
                        'emp_out': attend.check_out,
                    })

                # print("ateendedee=============>>>",self.attendance_brk_lines)
                # return {'domain': {'attendance_brk_lines': [('id', 'in', attendance_ids.ids)]}}
        if config_data == 'raw_data':
            # print("-----------------raw_data------------------")
            if self.currated_attendance_ref:
                # print("-----------------raw_data------------------",self.currated_attendance_ref)
                start_date = self.currated_attendance_ref.expected_start
                # print("-----------------raw_data------------------",start_date)
                end_date = self.currated_attendance_ref.expected_end
                row_data_ids = self.env['row.data'].search(
                    [('row_emp_name', '=', self.currated_attendance_ref.employee_id.id),
                     ('row_date_time', '>=', start_date),
                     ('row_date_time', '<=', end_date)
                    ])
                # print("-----------------raw_data------------------", row_data_ids)
                for attend in row_data_ids:
                    # self.attendance_brk_lines += attend
                    self.env['actual.row.attendance.line'].create({
                        'actual_row_id': self.id,
                        'employee_id': self.currated_attendance_ref.employee_id.id,
                        'emp_time' : attend.row_date_time,

                    })

                # print("ateendedee=============>>>",self.attendance_brk_lines)

class actual_break_informationLine(models.Model):
    _name='actual.break.information.line'

    actual_break_id = fields.Many2one('actual.break.information.wizard')
    employee_id = fields.Many2one('hr.employee', string='Employee ID')
    emp_in = fields.Datetime(string='IN')
    emp_out = fields.Datetime(string='OUT')
    emp_diff = fields.Float(string='Diff')

    @api.multi
    def set_in_as_checkin(self):
        if self.actual_break_id.currated_attendance_ref and self.emp_in:
            self.actual_break_id.currated_attendance_ref.check_in = self.emp_in

    @api.multi
    def set_in_as_checkout(self):
        if self.actual_break_id.currated_attendance_ref and self.emp_in:
            self.actual_break_id.currated_attendance_ref.check_out = self.emp_in

    @api.multi
    def set_out_as_checkin(self):
        if self.actual_break_id.currated_attendance_ref and self.emp_out:
            self.actual_break_id.currated_attendance_ref.check_in = self.emp_out

    @api.multi
    def set_out_as_checkout(self):
        if self.actual_break_id.currated_attendance_ref and self.emp_out:
            self.actual_break_id.currated_attendance_ref.check_out = self.emp_out


class ActualRowAttendanceLine(models.Model):
    _name='actual.row.attendance.line'

    actual_row_id = fields.Many2one('actual.break.information.wizard')
    employee_id = fields.Many2one('hr.employee', string='Employee ID')
    emp_time = fields.Datetime(string='Time')

    @api.multi
    def set_in_as_checkin(self):
        if self.actual_row_id.currated_attendance_ref and self.emp_time:
            self.actual_row_id.currated_attendance_ref.check_in = self.emp_time

    @api.multi
    def set_in_as_checkout(self):
        if self.actual_row_id.currated_attendance_ref and self.emp_time:
            self.actual_row_id.currated_attendance_ref.check_out = self.emp_time