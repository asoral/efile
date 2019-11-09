from odoo import fields, models, api, _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError

def convert_string_into_datetime(sting_date):
    datetime_value = datetime.strptime(sting_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=5,minutes=30, seconds=00)
    return datetime_value

class ProcessAttendanceWizard(models.Model):
    _name='process.attendance.wizard'
    _description = "Process Attendance"

    @api.onchange('date_range')
    def get_dates(self):
        for s in self:
            if s.date_range:
                s.from_date = s.date_range.date_start
                s.to_date = s.date_range.date_end


    date_range = fields.Many2one('date.range', 'Date range')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    employee_id = fields.Many2many('hr.employee', string='Employees')
    department_id = fields.Many2many('hr.department', string='Departments')
    process_by = fields.Selection([('employee', 'By Employee'),
                                   ('department', 'By Department'),], default="employee", string="Process By")


    @api.multi
    def process_attendance_button(self):
        # print("==================== enter in method========================")
        obj=self.env['hr.attendance.roster']
        if self.process_by =='employee':
#             print("============= by ep======process_attendance_button=====")
            if not self.employee_id:
                epm_ids = self.env['hr.employee'].search([])
                # print('============== emp not select then =========',epm_ids)

            if self.employee_id:
                epm_ids = self.employee_id
                # print('============== emp then =========', epm_ids)

            roster_ids = self.env['hr.attendance.roster'].search([('employee_id', 'in', epm_ids.ids),
                                                                  ('status','=','not_process'),('date','>=',self.from_date),('date','<=',self.to_date)])
#             print("========roster_ids========",roster_ids)


            data=obj.create_currated_attendance_records(roster_ids,check=False)

        if self.process_by == 'department':
            # print("============== by department=======")

            if not self.department_id:
                dpt_ids = self.env['hr.department'].search([])
                # print('============== dpt not select then =========', dpt_ids)

            if self.department_id:
                dpt_ids = self.department_id
                # print('============== dpt then =========', dpt_ids)

            roster_ids = self.env['hr.attendance.roster'].search([('employee_id.department_id', 'in', dpt_ids.ids),('date','>=',self.from_date),('date','<=',self.to_date)])
            # print("========roster_ids===department=====", roster_ids)
            data = obj.create_currated_attendance_records(roster_ids,check=False)



    # =====cron job========"
    def process_attendance_data(self):
        # print("=====cron job========")
        employee_ids = self.env['hr.employee'].search([])
        # print("========================================",datetime.today().strftime('%Y-%m-%d'))
#         old_date = date.today() - timedelta(3)
        
        yesterday = date.today() - timedelta(1)
        # print("========old_date================================",old_date)
        old_date = yesterday - timedelta(3)
        to_date = yesterday - timedelta(2)
        vals = {
            'from_date': old_date,
            'to_date':to_date,
            'process_by':'employee'
        }
#         'employee_id':employee_ids.ids,
        # print("----vals----------------------------------",vals)
        wizard_id = self.env['process.attendance.wizard'].create(vals)
        # print("---wizard_id----------------------------------------",wizard_id)
        wizard_id.process_attendance_button()
