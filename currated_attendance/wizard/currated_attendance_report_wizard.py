from odoo import fields, models, api, _

def tup_without_comma(tup):
    tup = tuple(tup)
    # print "666666666666555555555555555555555555555",tup
    if tup and len(tup) == 1:
        return '({0})'.format(tup[0])
    else:
        return tup

class CurratedAttendanceReport(models.Model):
    _name='currated.attendance.report'

    @api.onchange('date_range')
    def get_dates(self):
        for s in self:
            if s.date_range:
                s.from_date = s.date_range.date_start
                s.to_date = s.date_range.date_end

    date_range = fields.Many2one('date.range', 'Date range')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    report_type =fields.Selection([('summary', 'Summary'),
                                    ('detail', 'Detail')],
                                    string='Type',default='summary')
    employee_ids = fields.Many2many('hr.employee',string='Employee')
    department_ids = fields.Many2many('hr.department', string='Departments')
    employee_tag_ids = fields.Many2many('hr.employee.category',string='Employee Tag')

    def currated_attendance_report_button(self):

        if self.report_type == 'detail':
            if not self.employee_ids:
                emp_ids = self.env['hr.employee'].search([])
            if self.employee_ids:
                emp_ids = self.employee_ids

            if not self.department_ids:
                dept_ids = self.env['hr.department'].search([])
            if self.department_ids:
                dept_ids = self.department_ids

            if not self.employee_tag_ids:
                emp_tag_ids = self.env['hr.employee.category'].search([])
            if self.employee_tag_ids:
                emp_tag_ids = self.employee_tag_ids

            domain = [
                    ('expected_start', '>=', self.from_date),
                    ('expected_start', '<=', self.to_date),
                    ('expected_end', '<=', self.to_date),
                    ('expected_end', '>=', self.from_date),
                    ('employee_id','in',emp_ids.ids),'|',
                    ('department_id','in',(dept_ids.ids)),
                    ('department_id','=',False) , '|',
                    ('employee_id.category_ids','in',emp_tag_ids.ids),
                    ('employee_id.category_ids','=', False),
                    ]
            # print("---------------------domain",domain)
            currated_attendance_ids=self.env['currated.attendance'].search(domain)
            # for line in currated_attendance_ids:
            #     print("===========currated_attendance_ids=======================================",line.expected_start,self.from_date)
            return {
                'name': 'Currated Attendance',
                'view_type': 'form',
                'view_mode': 'tree,pivot,graph',
                'res_model': 'currated.attendance',
                'type': 'ir.actions.act_window',
                'nodestory': True,
                'domain': [('id', 'in', currated_attendance_ids.ids )],
                'target': 'current',
                'view': 'currated_attendance.currated_attendance_tree_view',
            }

        elif self.report_type == 'summary':
            previous_summary = self.env['currated.attendance.summary'].search([ ('user_id', '=', self.env.user.id),
            ('company_id', '=', self.env.user.company_id.id)])

            # print("------------------previous_summary----------------------------",previous_summary)
            previous_summary.unlink()
            # print("-----------print  summary report--------------------------")
            data = self.get_summary_report()
            return data





    # method to print currated attendance summary data
    def get_summary_report(self):
                        # print("---------method--print  summary report--------------------------")

                        if not self.employee_ids:
                            emp_ids = self.env['hr.employee'].search([])
                            # print("---------emp_ids----alll-----------",emp_ids)
                        if self.employee_ids:
                            emp_ids = self.employee_ids
                            # print("---------emp_ids-------selected--------",emp_ids)

                        if not self.department_ids:
                            dept_ids = self.env['hr.department'].search([])
                        if self.department_ids:
                            dept_ids = self.department_ids
                        # print("---------dept_ids---------------",dept_ids)


                        if not self.employee_tag_ids:
                            emp_tag_ids = self.env['hr.employee.category'].search([])
                        if self.employee_tag_ids:
                            emp_tag_ids = self.employee_tag_ids
                        # print("---------emp_tag_ids---------------",emp_tag_ids)

                        query= """insert into currated_attendance_summary(employee_id,biometric_id,identification_id,
                                                                        department_id,work_location,job_title,job_id,grade_id,
                                                                        expected_duty_hours,duty_hours,threshold_late_minute,user_id,company_id,working_days,absent_days,worked_days,no_of_late_coming,
                                                                        no_of_early_going,threshold_late_count,late_comming_minute,early_going_minute,over_time)
                                  select
                                        he.id as employee,
                                        he.bioid as bioid,
                                        he.identification_id as identification,
                                        he.department_id as department,
                                        he.work_location as work_loc,
                                        he.job_title as jobtitle,
                                        he.job_id as jobid,
                                        he.grade_id as grade,
                                        sum(ca.expected_duty_hours) as expecteddutyhr,
                                        sum(ca.duty_hours) as actualdutyhrs,
                                        sum(ca.threshold_late_minute) as thresholdlateminute,
                                        {0},
                                        {1},
                                        """.format(self.env.user.id,self.env.user.company_id.id)

                        query+="""(select count(*) from currated_attendance as xca 
                                          where xca.employee_id = he.id
                                          and xca.expected_start between '{0}' and '{1}'
                                          and xca.expected_end between '{0}' and '{1}'
                                  ) as workingdays,""".format(str(self.from_date),str(self.to_date))


                        query+="""(select count(*) from currated_attendance as xca 
                                          where xca.employee_id = he.id 
                                          and xca.absent is true
                                          and xca.expected_start between '{0}' and '{1}'
                                          and xca.expected_end between '{0}' and '{1}'
                                   ) as daysabsent,""".format(str(self.from_date),str(self.to_date))


                        query+="""(select count(*) from currated_attendance as xca 
                                          where xca.employee_id = he.id 
                                          and xca.absent is false
                                          and xca.expected_start between '{0}' and '{1}'
                                          and xca.expected_end between '{0}' and '{1}'
                                  ) as daysworked,""".format(str(self.from_date),str(self.to_date))



                        query+="""(select count(*) from currated_attendance as xca 
                                          where xca.employee_id = he.id 
                                          and xca.late_coming is true
                                          and xca.expected_start between '{0}' and '{1}'
                                          and xca.expected_end between '{0}' and '{1}'
                                  ) as numoflatecom,""".format(str(self.from_date),str(self.to_date))



                        query+="""(select count(*) from currated_attendance as xca 
                                          where xca.employee_id = he.id 
                                          and xca.early_going is true
                                          and xca.expected_start between '{0}' and '{1}'
                                          and xca.expected_end between '{0}' and '{1}'
                                   ) as numofearlygoing,""".format(str(self.from_date),str(self.to_date))

                        query += """(select count(*) from currated_attendance as xca
                                                  where xca.employee_id = he.id
                                                  and xca.threshold_late is true
                                                  and xca.expected_start between '{0}' and '{1}'
                                                  and xca.expected_end between '{0}' and '{1}'
                                           ) as numoflatethreshold,""".format(str(self.from_date), str(self.to_date))

                        query += """sum(ca.late_coming_min) as sumlatemin,
                                    sum(ca.early_going_min) as sumearlygoingmin,
                                    sum(ca.overtime_hours) as overtimehrs
                                        
                                   from currated_attendance as ca
                                    inner join hr_employee as he on ca.employee_id = he.id
                                    inner join employee_category_rel as ecr on ca.employee_id = ecr.emp_id
                                    inner join hr_employee_category as hec on ecr.category_id = hec.id

                      
                                   """
                        query+=""" where he.id in {0} """.format(tup_without_comma(emp_ids.ids))
                        query+=""" and COALESCE(he.department_id) in {0}  """.format(tup_without_comma(dept_ids.ids))
                        query+=""" and COALESCE(hec.id) in {0} """.format(tup_without_comma(emp_tag_ids.ids))
                        query+="""and ca.expected_start between '{0}' and '{1}' and ca.expected_end between '{0}' and '{1}' """.format(self.from_date,self.to_date)
                        query+="""group by he.id """
                        # print("----query-----------------------",query)

                        self.env.cr.execute(query)

                        action= {
                            'name': 'Currated Attendance Summary',
                            'view_type': 'form',
                            'view_mode': 'tree,pivot,graph',
                            'res_model': 'currated.attendance.summary',
                            'type': 'ir.actions.act_window',
                            'domain': [('user_id', '=', self.env.user.id), ('company_id', '=', self.env.user.company_id.id)],
                            'target': 'current',
                            'view': 'currated_attendance_summary_tree_view',
                            }
                        return action



