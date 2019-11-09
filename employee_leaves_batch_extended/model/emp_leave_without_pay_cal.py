from odoo import api, fields, models, _
import datetime
from datetime import datetime , timedelta, date
import time
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError

class HrHolidayStatus(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'Payslip Holidyas'
    
#     lwp = fields.Boolean(string="LWP")

class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _inherit = 'hr.payslip.employees'
    
    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note','lwp_date_from','lwp_date_to'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        lwp_from_date = run_data.get('lwp_date_from')
        lwp_to_date = run_data.get('lwp_date_to')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
#             print("????????????????????#####################?????????????????????",slip_data)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'lwp_date_from':lwp_from_date,
                'lwp_date_to':lwp_to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}


class HRPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    lwp_date_from = fields.Date(string='Date From', readonly=True, required=True,
        default=time.strftime('%Y-%m-01'), states={'draft': [('readonly', False)]})
    lwp_date_to = fields.Date(string='Date To', readonly=True, required=True,
        default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        states={'draft': [('readonly', False)]})
    
    
class HrPayslip(models.Model): 
    _inherit = 'hr.payslip'
    
    lwp_count = fields.Float('Number of Leaves',compute='onchange_employee_leaves_count')  
    lwp_att = fields.Float('Attendance',compute='onchange_employee_leave_attendance')
    lwp_attend = fields.Float(compute='onchange_employee_leave_attendance')
    
    lwp_date_from = fields.Date(string='Date From', readonly=True, required=True,
        default=time.strftime('%Y-%m-01'), states={'draft': [('readonly', False)]})
    lwp_date_to = fields.Date(string='Date To', readonly=True, required=True,
        default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        states={'draft': [('readonly', False)]})
    
    
    @api.multi
    @api.depends('employee_id')
    def onchange_employee_leaves_count(self):
#         self.ensure_one()
        leaves_count = 0.0
        for leave in self:
            domain =[('employee_id','=',leave.employee_id.id),('holiday_status_id.unpaid', '=', True),('state','!=', 'refuse'),('date_from','>=',leave.lwp_date_from),('date_to','<=',leave.lwp_date_to)]
#             print("??????????????????????????????",domain)
            emp_lwp_lines = self.env['hr.leave'].search(domain)
#             print("domainmethodemployeeiddddddddddddddd",emp_lwp_lines)
            if emp_lwp_lines:
                for lwp in emp_lwp_lines:
                    if lwp.holiday_status_id.unpaid == True:
                            leaves_count += lwp.number_of_days_display
#                             print("lwpwpwpwpwpwpwpwpwpwpwwpwpwpwpwp",leaves_count)
                leave.lwp_count = leaves_count
#                 print("totalnoofclalalalalalalal",leave.lwp_count)
    
    def onchange_employee_leave_attendance(self):
        for s in self:
            if s.date_from and s.date_to:
                DATETIME_FORMAT = "%Y-%m-%d"
                from_date = s.date_from
                to_date = s.date_to
                s.lwp_attend = (to_date - from_date ).days + 1
                s.lwp_att = s.lwp_attend - s.lwp_count

    def convert_date(x,y,z):
        orig_date = datetime.datetime(x,y,z)
        orig_date = str(orig_date)
        d = datetime.datetime.strptime(orig_date, '%Y-%m-%d %H:%M:%S')
        d = d.strftime('%m/%d/%y')
        return d


    @api.multi
    def hr_employee_lwp_request_leave_left(self):
        
        return{
            'name': _('Leaves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.leave',
            'src_model' : 'hr.employee',
            'type': 'ir.actions.act_window',
            'domain':[('employee_id','=',self.employee_id.id),('holiday_type','=','employee'), ('holiday_status_id.unpaid', '=', True),('state','!=', 'refuse')],
            'context': {'search_default_employee_id': self.employee_id.id, 'default_employee_id': self.employee_id.id, 'search_default_group_type': 1,
                'search_default_year': 1},
            'search_view_id' : self.env.ref('hr_holidays.view_hr_holidays_filter').id
            }
        
    @api.multi
    def hr_employee_lwp_request_leave_attendance(self):
        
        return{
            'name':_('Attendance'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'hr.attendance',
            'src_model':'hr.employee',
            'type':'ir.actions.act_window',
            'domain':[('employee_id','=',self.employee_id.id)],
            'context': {'search_default_employee_id': self.employee_id.id, 'default_employee_id': self.employee_id.id, 'search_default_group_type': 1,
                'search_default_year': 1},
            'search_view_id':self.env.ref('hr_attendance.hr_attendance_view_filter').id
            
            }
    
    @api.multi
    def hr_employee_lwp_request_leave_diff(self):
        
        return{
            }
