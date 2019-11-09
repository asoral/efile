# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import math

# This will generate 16th of days

class EmpAtteWizard(models.TransientModel):
    _name = 'wizard.emp.attedance'
    _description = 'Wizard Emp Atten'
    
    
    date_range = fields.Many2one('date.range','Date range')
    date_from = fields.Date(string="Date From",required=True)
    date_to = fields.Date(string="Date To",required=True)
    
    
    emp_ids = fields.Many2many('hr.employee',string="Employee")
    total_working_days = fields.Integer(string="Working Days")
    present_days = fields.Integer(string="Present Days")

    @api.onchange('date_range')
    def get_dates(self):
        for s in self:
            if s.date_range:
                s.date_from = s.date_range.date_start
                s.date_to = s.date_range.date_end

    def add_time_zone(self,date):
        # print("--------------------sting_date--------------------",sting_date)
        datetime_value = date + timedelta(hours=5, minutes=30, seconds=00)
        return datetime_value

    def get_emp_ids(self):
        emp_ids = self.env['hr.employee']
        if not self.emp_ids:
            emp_ids = self.env['hr.employee'].search([])
        else:
            emp_ids = self.emp_ids
        return emp_ids

    @api.model
    def value_to_html(self, value):
        sign = math.copysign(1.0, value)
        hours, minutes = divmod(abs(value) * 60, 60)
        minutes = round(minutes)
        if minutes == 60:
            minutes = 0
            hours += 1
        return '%d:%02d' % (sign * hours, minutes)

    def _get_months(self):
        # it works for geting month name between two dates.
        res = []
        start_date = fields.Date.from_string(self.date_from)
        end_date = start_date + relativedelta(days=self.get_month_days())
        while start_date <= end_date:
            last_date = start_date + relativedelta(day=1, months=+1, days=-1)
            if last_date > end_date:
                last_date = end_date
            month_days = (last_date - start_date).days + 1
            res.append({'month_name': start_date.strftime('%B'), 'days': month_days})
            start_date += relativedelta(day=1, months=+1)
        
        print("===res",res)
        return res

    def _date_is_day_off(self, date,emp):
        list = []
        for off in emp.weekoff_ids:
            week_int = self.dayNameFromWeekday(off.name)
            list.append(week_int)
        # return date.weekday() in (calendar.SATURDAY, calendar.SUNDAY,)
        return date.weekday() in list

    def _get_day(self,emp):
        res = []
        start_date = fields.Date.from_string(self.date_from)
        self.total_working_days = 0
        for x in range(0,self.get_month_days()+1):

            color = ''
            color = '#ababab' if self._date_is_day_off(start_date,emp) else ''
#             if self._date_is_day_off(start_date, emp):
#                 color = '#ababab'
#             else:
#                 self.total_working_days += 1
            self.total_working_days += 1
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day , 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res

    def _get_attendance(self,emp):
        res = []
        start_date = fields.Date.from_string(self.date_from)
        self.present_days = 0
        for x in range(0,self.get_month_days()+1):
            check_in = check_out = ''
            color = ''
            present = "A"

            curated_ids = self.env['currated.attendance'].search([('employee_id','=',emp.id),
                                                                  ('expected_start','>=',start_date),('expected_end','<=',start_date)],limit = 1)
            if self._date_is_day_off(start_date,emp):
                present = 'WO'
            if curated_ids.check_in and curated_ids.check_out:
                present = "P"
                
                # print("======ids", curated_ids)
                if curated_ids.check_in:
                    check_in_timez = self.add_time_zone(curated_ids.check_in)
                    check_in= "" +str(check_in_timez.hour) + "." + str(check_in_timez.minute)
                if curated_ids.check_out:
                    check_out_timez = self.add_time_zone(curated_ids.check_out)
                    check_out = "" + str(check_out_timez.hour) + "." + str(check_out_timez.minute)

            # print("===dict",dict)

            leaves = self.env['hr.leave']
            if not curated_ids:
                leaves = leaves.search([('date_from', '<=', start_date), ('date_to', '>=', start_date),
                                                      ('state', '=', 'validate'), ('employee_id', '=', emp.id)],limit=1)
                # print("====test_leave", leaves)
                if leaves:
                    present = "L"
                    color = leaves.holiday_status_id.color_name
            
            if present != "A":
                if leaves:
                    if leaves.holiday_status_id.unpaid == False:
                        self.present_days += 1
                else:
                    self.present_days += 1

            res.append( {'present': present, 'color': color,
                         'check_in':check_in,
                         'check_out':check_out,
                         'duty_hours':self.value_to_html(curated_ids.duty_hours) if curated_ids.duty_hours > 0.0 else '',
                         'late_coming': self.value_to_html(curated_ids.late_coming_min) if curated_ids.late_coming_min > 0.0 else '',
                         'early_going': self.value_to_html(curated_ids.early_going_min) if curated_ids.early_going_min > 0.0 else '',
                         'overtime': self.value_to_html(curated_ids.overtime_hours) if curated_ids.overtime_hours > 0.0 else '',
                         })

            start_date = start_date + relativedelta(days=1)
        return  res


    def _get_data_from_report(self, data):
        res = []
        Employee = self.env['hr.employee']

        res.append({'data': []})
        for emp in Employee.browse(data['emp']):
            res[0]['data'].append({
                'emp': emp.name,
                'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
                'sum': self.sum
            })
        return res


    def report_pdf(self):
        report_id = self.env['ir.actions.report']
        context = self.env.context
        report_id = self.env['ir.actions.report'].with_context(context).search(
                [('report_name', '=', 'emp_attedance_report.report_emp_attendance')], limit=1)
            
        if not report_id:
            raise UserError(
                _("Bad Report Reference") + _("This report is not loaded into the database: "))
        print("--------------",report_id)
        
        return {
            'context': context,
            'type': 'ir.actions.report',
            'report_name': report_id.report_name,
            'report_type': report_id.report_type,
            'report_file': report_id.report_file,
            'name': report_id.name,
                }

    def _get_holidays_status(self):
        res = []
        for holiday in self.env['hr.leave.type'].search([]):
            res.append({'color': holiday.color_name, 'name': holiday.name})
        return res


    def dayNameFromWeekday(self,weekday):
        if weekday == "Monday":
            return 0
        if weekday == "Tuesday":
            return 1
        if weekday == "Wednesday":
            return 2
        if weekday == "Thursday":
            return 3
        if weekday == "Friday":
            return 4
        if weekday == "Saturday":
            return 5
        if weekday == "Sunday":
            return 6



    def get_month_days(self):
        delta = self.date_to - self.date_from
        return delta.days if delta.days <= 31 else 31
