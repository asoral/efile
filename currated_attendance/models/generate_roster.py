from odoo import api, models,fields
from odoo.exceptions import ValidationError, AccessError
from odoo import exceptions
import calendar
from datetime import datetime, timedelta
import logging
import calendar

_logger = logging.getLogger(__name__)

class GenerateRoaster(models.Model):
    _name='generate.hr.attendance.roaster'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Generate Attendance Roaster"

    @api.onchange('date_range')
    def get_dates(self):
        if self.date_range:
            self.from_date = self.date_range.date_start
            self.to_date = self.date_range.date_end

    date_range = fields.Many2one('date.range', string='Date range')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')


    employee_ids = fields.Many2many('hr.employee', string='Employees',track_visibility='always')
    department_ids = fields.Many2many('hr.department', string='Departments')
    category_ids = fields.Many2many('hr.employee.category', string='Categories')
    state = fields.Selection([('draft','Draft'),
                              ('approval','Approval'),
                              ('approved','Approved'),
                              ('amendment','Amendment')],string="State",default="draft",readonly="1")
    mode_type = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Mode', required=True, default='employee',
        help="Allow to create requests in rosters:"
             "\n- By Employee: for a specific employee"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category")

    roster_lines = fields.One2many('roster.employee.shifts.values','generate_roster_ref',string="Lines")
    roster_lines_ids = fields.One2many('roster.employee.shift.values.line','generate_roster_ref_line',string="Roaster Lines")

    # added by priyanka as per task(TASK1065)
    @api.multi
    def unlink(self):
        for roster in self:
            if roster.state == 'approved':
                raise ValidationError('You can not delete a Roster in Approved state')
        return super(GenerateRoaster, self).unlink()

    @api.onchange('department_ids')
    def _get_department_employees(self):
        if self.department_ids:
            departments = self.department_ids
            employees = self.env['hr.employee'].search([('department_id', 'in', departments.ids)])
            # self.employee_ids += employees
            self.update({'employee_ids': [(6, 0, employees.ids)]})

    @api.multi
    # @api.constrains('mode_type','employee_ids','department_ids','category_ids','from_date','to_date')
    # @api.onchange('employee_ids','department_ids','category_ids','mode_type','from_date','to_date')
    def get_the_employees(self):
        # employees = self.env['hr.employee']
        # if self.mode_type == 'employee':
        #     # print("Mode type=====employee===>>>", self.mode_type)
        #     if not self.employee_ids:
        #         employees = self.env['hr.employee'].search([])
        #     if self.employee_ids:
        #         employeess = self.employee_ids
        #         employees = self.env['hr.employee'].search([('id','in',employeess.ids)])
        #
        # if self.mode_type == 'department':
        #     # print("Mode type=====department===>>>", self.mode_type)
        #     if not self.department_ids:
        #         departments = self.env['hr.department'].search([])
        #         employees = self.env['hr.employee'].search([('department_id','in',departments.ids)])
        #     if self.department_ids:
        #         departments = self.department_ids
        #         if not self.employee_ids:
        #             employees = self.env['hr.employee'].search([('department_id', 'in', departments.ids)])
        #             self.update({'employee_ids': [(6, 0, employees.ids)]})
        #         else:
        #             employeess = self.employee_ids
        #             employees = self.env['hr.employee'].search([('id', 'in', employeess.ids)])
        #
        # if self.mode_type == 'category':
        #     # print("Mode type======category==>>>", self.mode_type)
        #     if not self.category_ids:
        #         category = self.env['hr.employee.category'].search([])
        #         employees = self.env['hr.employee'].search([('category_ids','in',category.ids)])
        #     if self.category_ids:
        #         category = self.category_ids
        #         employees = self.env['hr.employee'].search([('category_ids', 'in', category.ids)])
        # if self.roster_lines:
        self.roster_lines.unlink()

        if self.to_date and self.from_date:
            lines=self.env['roster.employee.shift.values.line'].search([('generate_roster_ref_line','=',self.id)])
            # print("employees===========>>>>",lines)
            # born = self.from_date.weekday()
            # print("---------------------calendar.day_name[born]",calendar.day_name[born])

            delta = self.to_date - self.from_date  # timedelta
            # print("Delta===========>>",delta)
            sun =[]
            mon =[]
            teu =[]
            wed =[]
            thu =[]
            fri =[]
            sat =[]
            for i in range(delta.days + 1):
                dates = self.from_date + timedelta(days=i)
                dd = dates.weekday()
                born = calendar.day_name[dd]
                # print("---------------------calendar.day_name[born]", born)
                if born == 'Sunday':
                    sun.append(dates)
                if born == 'Monday':
                    mon.append(dates)
                if born == 'Tuesday':
                    teu.append(dates)
                if born == 'Wednesday':
                    wed.append(dates)
                if born == 'Thursday':
                    thu.append(dates)
                if born == 'Friday':
                    fri.append(dates)
                if born == 'Saturday':
                    sat.append(dates)

            for i in range(delta.days + 1):
                # print("Dates---------->>>", self.from_date + timedelta(days=i))
                dd =self.from_date + timedelta(days=i)
                for emp in lines:
                    # print("employeees mile h bhai========>>>", emp.name)

                    if emp.sunday and dd in sun:
                        self.create_roaster_value(emp.employee_id,dd,emp.sunday)

                    elif emp.monday and dd in mon:
                        self.create_roaster_value(emp.employee_id, dd, emp.monday)

                    elif emp.tuesday and dd in teu:
                        self.create_roaster_value(emp.employee_id, dd, emp.tuesday)

                    elif emp.wednesday and dd in wed:
                        self.create_roaster_value(emp.employee_id, dd, emp.wednesday)

                    elif emp.thursday and dd in thu:
                        self.create_roaster_value(emp.employee_id, dd, emp.thursday)

                    elif emp.friday and dd in fri:
                        self.create_roaster_value(emp.employee_id, dd, emp.friday)

                    elif emp.saturday and dd in sat:
                        self.create_roaster_value(emp.employee_id, dd, emp.saturday)

                    else:
                        self.env['roster.employee.shifts.values'].create({
                            'generate_roster_ref': self.id,
                            'employee_id': emp.employee_id.id,
                            'shift_id': emp.working_time_id.id,
                            'date': self.from_date + timedelta(days=i),
                        })

    def create_roaster_value(self,emp,dd,shift_id):
        self.env['roster.employee.shifts.values'].create({
            'generate_roster_ref': self.id,
            'employee_id': emp.id,
            'shift_id':shift_id.id,
            'date': dd,
        })

    @api.multi
    # @api.constrains('mode_type','employee_ids','department_ids','category_ids','from_date','to_date')
    # @api.onchange('employee_ids','department_ids','category_ids','mode_type','from_date','to_date')
    def get_the_employees_new(self):
        employees = self.env['hr.employee']
        if self.mode_type == 'employee':
            # print("Mode type=====employee===>>>", self.mode_type)
            if not self.employee_ids:
                employees = self.env['hr.employee'].search([])
            if self.employee_ids:
                employeess = self.employee_ids
                employees = self.env['hr.employee'].search([('id','in',employeess.ids)])
                # print("employeeee=====>",employees)
        if self.mode_type == 'department':
            # print("Mode type=====department===>>>", self.mode_type)
            if not self.department_ids:
                departments = self.env['hr.department'].search([])
                employees = self.env['hr.employee'].search([('department_id','in',departments.ids)])
            if self.department_ids:
                departments = self.department_ids
                if not self.employee_ids:
                    employees = self.env['hr.employee'].search([('department_id', 'in', departments.ids)])
                    self.update({'employee_ids': [(6, 0, employees.ids)]})
                else:
                    employeess = self.employee_ids
                    employees = self.env['hr.employee'].search([('id', 'in', employeess.ids)])

        if self.mode_type == 'category':
            # print("Mode type======category==>>>", self.mode_type)
            if not self.category_ids:
                category = self.env['hr.employee.category'].search([])
                employees = self.env['hr.employee'].search([('category_ids','in',category.ids)])
            if self.category_ids:
                category = self.category_ids
                employees = self.env['hr.employee'].search([('category_ids', 'in', category.ids)])
        if self.roster_lines_ids:
            self.roster_lines_ids.unlink()

#         if self.to_date and self.from_date:
#             print("Dates===========>>>>",self.to_date,self.from_date)
#             delta = self.to_date - self.from_date  # timedelta
#             print("Delta===========>>",delta)
#             for i in range(delta.days + 1):
#                 print("Dates---------->>>", self.from_date + timedelta(days=i))
        if self.mode_type:
            for emp in employees:
                # print("employeees mile h bhai========>>>", emp.name)
                res = self.env['roster.employee.shift.values.line'].create({
                    'generate_roster_ref_line': self.id,
                    'employee_id': emp.id,
#                         'date':self.from_date + timedelta(days=i),
                })
#                 self.roster_lines_ids = res
#                     self.roster_lines_ids = res



    @api.multi
    def send_for_approval(self):
        self.write({
            'state': 'approval',
        })

    @api.multi
    def send_to_amendment(self):
        self.write({
            'state': 'amendment'
        })

    #name_get
    @api.multi
    def name_get(self):
        result = []
        name = ''
        for record in self:
            name = (str(record.from_date) + ' to ' + str(record.to_date))
            result.append((record.id, name))
        return result

    @api.multi
    def confirm_approved(self):
        self.get_the_employees()
        # if self.to_date and self.from_date:
            # print("Dates===========>>>>",self.to_date,self.from_date)
            # delta = self.to_date - self.from_date  # timedelta
            # print("Delta===========>>",delta)
#             for i in range(delta.days + 1):
#                 print("Dates---------->>>", self.from_date + timedelta(days=i))
#                 for rlines in self.roster_lines_ids:
#                     rosline = self.env['hr.attendance.roster'].create({
#                         'date':self.from_date + timedelta(days=i),
#                         'employee_id': rlines.employee_id.id,
#                         'shift_id': rlines.working_time_id.id,
# #                         'shift_line_ids': [(6, 0, rlines.shift_line_ids.ids)],
#                     })
        for rlines in self.roster_lines:
            # print("=====Lines from ===================",rlines)
            rosline = self.env['hr.attendance.roster'].create({
                'date':rlines.date,
                'employee_id': rlines.employee_id.id,
                'shift_id': rlines.shift_id.id,
                'shift_line_ids': [(6, 0, rlines.shift_line_ids.ids)],
            })
            # rosline.find_shift_hour()

        self.write({
            'state': 'approved',
        })

class RoasterEmployeeShiftValuesLine(models.Model):
    _name = "roster.employee.shift.values.line"
    _description = "Roaster Employee Shift Values Lines"
    
    generate_roster_ref_line = fields.Many2one('generate.hr.attendance.roaster',string="Generate Roaster")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    date =fields.Date(string="Date")
    emp_code = fields.Char(string="Employee Code")
    dep_id = fields.Many2one('hr.department',string="Department")
    working_time_id = fields.Many2one('resource.calendar',string="Working Time")
    night_shift = fields.Boolean(string="Night Shift")
    sunday = fields.Many2one('resource.calendar',string="Sunday")
    monday = fields.Many2one('resource.calendar',string="Monday")
    tuesday = fields.Many2one('resource.calendar',string="Tuesday")
    wednesday = fields.Many2one('resource.calendar',string="Wednesday")
    thursday = fields.Many2one('resource.calendar',string="Thursday")
    friday = fields.Many2one('resource.calendar',string="Friday")
    saturday = fields.Many2one('resource.calendar',string="Saturday")
    weekly_off_ids = fields.Many2many('employee.weekoff',string="Weekly Offs")
    sun = fields.Boolean(string="Sun")
    mon = fields.Boolean(string="Mon")
    tue = fields.Boolean(string="Tue")
    wen = fields.Boolean(string="Wen")
    thu = fields.Boolean(string="Thu")
    fri = fields.Boolean(string="Fri")
    sat = fields.Boolean(string="Sat")
    
    @api.constrains('weekly_off_ids')
    @api.onchange('weekly_off_ids')
    def get_weekly_off(self):
        for s in self:
            s.sun =False
            s.mon =False
            s.tue =False
            s.wen =False
            s.thu =False
            s.fri =False
            s.sat =False
            for week in s.weekly_off_ids:
                if week.name == 'Sunday':
                    # print("sundaaaaaaaaaaaaaaaa",s.weekly_off_ids.name)
                    s.sun = True
                elif week.name == 'Monday':
                    s.mon = True
                elif week.name == 'Tuesday':
                    s.tue = True
                elif week.name == 'Wednesday':
                    s.wen = True
                elif week.name == 'Thursday':
                    s.thu = True
                elif week.name == 'Friday':
                    s.fri = True
                elif week.name == 'Saturday':
                    s.sat = True
               
    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def get_shift_from_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.emp_code = rec.employee_id.identification_id
                rec.dep_id = rec.employee_id.department_id.id
                rec.working_time_id = rec.employee_id.resource_calendar_id.id
#                 rec.sunday = rec.employee_id.resource_calendar_id.id
                rec.night_shift = rec.employee_id.resource_calendar_id.night_shift
                rec.weekly_off_ids = rec.employee_id.weekoff_ids.ids

    @api.constrains('working_time_id','weekly_off_ids')
    @api.onchange('working_time_id','weekly_off_ids')
    def change_week_working_time(self):
        for rec in self:
            # print('-------1------------',rec.employee_id.resource_calendar_id,rec.employee_id.weekoff_ids)
            if rec.working_time_id:
                rec.employee_id.update({'resource_calendar_id':rec.working_time_id.id})
            if rec.weekly_off_ids:
                rec.employee_id.update({'weekoff_ids':rec.weekly_off_ids.ids})
            # print('-------2------------', rec.employee_id.resource_calendar_id, rec.employee_id.weekoff_ids)

class RosterEmployeeShiftsValues(models.Model):
    _name = "roster.employee.shifts.values"
    _description = "Roster Employee Shifts Values"

    generate_roster_ref = fields.Many2one('generate.hr.attendance.roaster',string="Generate roaster ref")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    shift_id = fields.Many2one('resource.calendar',string="Shift")
    date =fields.Date(string="Date")
    shift_line_ids = fields.Many2many('resource.calendar.attendance', string="Shift Line",domain="[('calendar_id','=',shift_id)]")
    hour_from = fields.Float(string='Work from', help="Start and End time of working.")
    hour_to = fields.Float(string='Work to')

    # @api.constrains('date')
    # @api.onchange('date')
    # def get_shift_from_employee(self):
    #     for rec in self:
    #         if rec.employee_id:
    #             rec.shift_id = rec.employee_id.resource_calendar_id.id

    @api.constrains('date')
    @api.onchange('date')
    def get_weekday_from_date(self):
        for record in self:
            # weekday = calendar.day_name[]
            # print("date==================>>>>",record.date.weekday())
            shiftlines = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(record.date.weekday())),('calendar_id','=',record.shift_id.id)])
            # print("========shiftline======Got===",shiftlines)
            record.shift_line_ids = shiftlines

    # @api.constrains('shift_line_id')
    # @api.onchange('shift_line_id')
    # def find_shift_hour(self):
    #     for s in self:
    #         if s.shift_line_id:
    #             s.hour_from = s.shift_line_id.hour_from
    #             s.hour_to = s.shift_line_id.hour_to

