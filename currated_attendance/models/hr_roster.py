from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


def convert_string_into_datetime(sting_date):
    # print("--------------------sting_date--------------------",sting_date)
    datetime_value = datetime.strptime(sting_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=5,minutes=30, seconds=00)

    return datetime_value


class HrAttendanceRoster(models.Model):
    _name = 'hr.attendance.roster'
    _description = "Employee roster"

    employee_id = fields.Many2one('hr.employee',string="Employee")
    date = fields.Date(string="Date")
    shift_id = fields.Many2one('resource.calendar',string="Shift Name")
    shift_line_ids = fields.Many2many('resource.calendar.attendance',string="Shift Line",domain="[('calendar_id','=',shift_id)]")
    # hour_from = fields.Float(string='Work from', help="Start and End time of working.")
    # hour_to = fields.Float(string='Work to')
    status = fields.Selection([
        ('processed', 'Processed'),
        ('not_process', 'Not Process')],string='Status',default='not_process')

    @api.multi
    def name_get(self):
        result = []
        name = ''
        for record in self:
            name = (str(record.employee_id.name) + '-' + str(record.shift_id.name))
            result.append((record.id, name))
        return result

    # @api.constrains('shift_line_id')
    # @api.onchange('shift_line_id')
    # def find_shift_hour(self):
    #     for s in self:
    #         if s.shift_line_id:
    #             s.hour_from=s.shift_line_id.hour_from
    #             s.hour_to = s.shift_line_id.hour_to

    @api.multi
    def create_currated_attendance_records(self,recordslines,check):
        for record in recordslines:
#             print("===record.status=",record.status,"====check =",check)
            if record.status=='not_process' or check == True:
#                 print("-----------record--------------------",record)
                vals = self.create_vals(record)
                
                if check == True:
#                     print("======check===============")
                    currated_record = self.env['currated.attendance'].search([('employee_id','=',vals['employee_id']),
                                                                              ('check_in','=',vals['check_in']),
                                                                              ('check_out','=',vals['check_out']),
                                                                              ('roster_id','=',vals['roster_id'])
                                                                            ])
                    print("===currated_record",currated_record)
                    if currated_record:
                        currated_record.unlink()
                    
                if vals:
                    res = self.env['currated.attendance'].create(vals)
                    if res:
                        record.status = 'processed'

    def create_vals(self, record):
        config_data = self.env['ir.config_parameter'].sudo().get_param(
            'currated_attendance.source_attendance_data_from')
        # print("-------------config_data-----------------------------------",config_data)

        if record.shift_line_ids:
            for shift in record.shift_line_ids:
                # config_values = self.env['ir.config_parameter'].sudo().get_param('currated_attendance.buffer_time_float')
                config_values = shift.calendar_id.buffer_time_float
                new = shift.hour_from + float(config_values)
                max_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new * 60, 60))
                # print("------float(config_values)565754765-------------", shift.hour_from,float(config_values))
                new1 = shift.hour_from - float(config_values)
                # new1 = float(config_values) - shift.hour_from
                # print("--------new1---------------------", new1)
                min_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new1 * 60, 60))
                # print("---------min_start_time---------------------", min_start_time)

                new2 = shift.hour_to + float(config_values)
                max_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new2 * 60, 60))
                new3 = shift.hour_to - float(config_values)
                min_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new3 * 60, 60))

#                 str_min_day_checkin = str(record.date) + ' ' + min_start_time + ':00'
#                 str_max_day_checkin = str(record.date) + ' ' + max_start_time + ':00'
#                 str_min_day_checkout = str(record.date) + ' ' + min_end_time + ':00'
#                 str_max_day_checkout = str(record.date) + ' ' + max_end_time + ':00'
                
                str_min_day_checkin = str(record.date) +' '+  '00:00:00'
                str_max_day_checkin = str(record.date) +' '+  '00:00:00'
                str_min_day_checkout = str(record.date)+' ' +  '00:00:00'
                str_max_day_checkout = str(record.date) +' '+  '00:00:00'
                # print("---------str_min_day_checkin--------------------------------",record.date,min_start_time,str_min_day_checkin)
                min_day_checkin = convert_string_into_datetime(str_min_day_checkin)
                max_day_checkin = convert_string_into_datetime(str_max_day_checkin)
                min_day_checkout = convert_string_into_datetime(str_min_day_checkout)
                max_day_checkout = convert_string_into_datetime(str_max_day_checkout)
                # print(":======max_start_time",max_start_time)
                min_day_checkin += timedelta(hours=new1)  #new1 use for min_start_time
                max_day_checkin += timedelta(hours=new)  #new use for max_start_time
                min_day_checkout +=timedelta(hours=new3)  #new3 use for min_end_time
                max_day_checkout += timedelta(hours=new2)  #new2 use for max_end_time
                
                expected_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(shift.hour_from * 60, 60))
                expected_checkin = convert_string_into_datetime(str(record.date) + ' ' + expected_time + ':00')
                expected_time2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(shift.hour_to * 60, 60))
                # expected_checkout = convert_string_into_datetime(str(record.date) + ' ' + expected_time2 + ':00')
                expected_checkout = expected_checkin + timedelta(hours=shift.calendar_id.hours_per_day)
                print("------------expected_checkout--------------------",expected_checkout)

                if config_data == 'attendance':
                    checkin_attendance_id_utc = self.env['hr.attendance'].search([('employee_id', '=', record.employee_id.id),
                                                                              ('check_in', '>=', min_day_checkin),
                                                                              ('check_in', '<=', max_day_checkin)], limit=1,
                                                                             order="check_in asc")


                    checkout_attendance_id_utc = self.env['hr.attendance'].search([('employee_id', '=', record.employee_id.id),
                                                                               ('check_out', '>=', min_day_checkout),
                                                                               ('check_out', '<=', max_day_checkout)], limit=1,
                                                                              order="check_out desc")

                    # print("--------shift-------attendance--------------",checkin_attendance_id_utc, checkout_attendance_id_utc)
                    # print("--------shift-------attendance--------------",checkin_attendance_id_utc.check_in, checkout_attendance_id_utc.check_out)
                    return {
                        'employee_id': record.employee_id.id,
                        'check_in': checkin_attendance_id_utc.check_in if checkin_attendance_id_utc else False,
                        'check_out': checkout_attendance_id_utc.check_out if checkout_attendance_id_utc else False,
                        'department_id': record.employee_id.department_id.id,
                        # 'operating_unit_id': record.employee_id.operating_unit_id.id,
                        'expected_start': expected_checkin,
                        'expected_end': expected_checkout,
                        'roster_id': record.id,
                    }

                if config_data == 'raw_data':
                    checkin_attendance_id_utc = self.env['row.data'].search([('row_emp_name', '=', record.employee_id.id),
                                                                                ('row_date_time', '>=', min_day_checkin),
                                                                                ('row_date_time', '<=', max_day_checkin)], limit=1,
                                                                            order="row_date_time asc")
                    # print("---------row------checkin_attendance_id_utc-----------------------",checkin_attendance_id_utc)

                    checkout_attendance_id_utc = self.env['row.data'].search([
                                                                                ('row_emp_name', '=', record.employee_id.id),
                                                                                ('row_date_time', '>=', min_day_checkout),
                                                                                ('row_date_time', '<=', max_day_checkout)], limit=1,
                                                                            order="row_date_time desc")
                    # print("------row---------checkout_attendance_id_utc-----------------------",checkout_attendance_id_utc)

                    return {
                        'employee_id': record.employee_id.id,
                        'check_in': checkin_attendance_id_utc.row_date_time if checkin_attendance_id_utc else False,
                        'check_out': checkout_attendance_id_utc.row_date_time if checkout_attendance_id_utc else False,
                        'department_id': record.employee_id.department_id.id,
                        # 'operating_unit_id': record.employee_id.operating_unit_id.id,
                        'expected_start': expected_checkin,
                        'expected_end': expected_checkout,
                        'roster_id': record.id,
                    }
    
    
    def process_attendance_action(self):
#         ids = self.filtered(lambda x:x.status == 'not_process')
#         employee_ids = self.mapped('employee_id')
#         
#         f_date = t_date = self[0].date
#         for s in self:
#             if s.date > t_date:
#                 t_date = s.date
#         vals = {
#             'from_date': f_date,
#             'to_date':t_date,
#             'process_by':'employee',
#             'employee_id':employee_ids.ids
#         }
#         wizard_id = self.env['process.attendance.wizard'].create(vals)
#         wizard_id.process_attendance_button()
        
        self[0].create_currated_attendance_records(self,check=True)

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    night_shift = fields.Boolean(string="Night Shift")

    buffer_time_float = fields.Float(string="Buffer Time",help="This field helps to Add the Buffer Time In Login")


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    @api.multi
    def name_get(self):
        result = []
        name = ''
        for record in self:
            name=dict(record._fields['dayofweek'].selection).get(record.dayofweek)
            result.append((record.id, name))
        return result





#old code before adding many2many shift lines working fine
        # print("================ in vals method===========", record.date,)
        # config_values = self.env['base.config.settings'].search([], limit=1, order="id desc")
        # print("Buffer_time============>>>", config_values.buffer_time_float,record.hour_from - config_values.buffer_time_float,float(record.hour_from - config_values.buffer_time_float))
        # new = record.hour_from + config_values.buffer_time_float
        # max_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new * 60, 60))
        # new1 = record.hour_from - config_values.buffer_time_float
        # min_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new1 * 60, 60))
        # print("----------------------min_start_time--------------max_start_time--------->>>>", min_start_time, max_start_time)
        #
        # new2 = record.hour_to + config_values.buffer_time_float
        # max_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new2 * 60, 60))
        # new3 = record.hour_to - config_values.buffer_time_float
        # min_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(new3 * 60, 60))
        # print("---------------------min_end_time--------------max_end_time--------->>>>", min_end_time, max_end_time)
        #
        # str_min_day_checkin = str(record.date) + ' ' + min_start_time + ':00'
        # str_max_day_checkin = str(record.date) + ' ' + max_start_time + ':00'
        # str_min_day_checkout = str(record.date) + ' ' + min_end_time + ':00'
        # str_max_day_checkout = str(record.date) + ' ' + max_end_time + ':00'
        # print("String dates check in=============>>>>",str_min_day_checkin,str_max_day_checkin)
        #
        # min_day_checkin = convert_string_into_datetime(str_min_day_checkin)
        # max_day_checkin = convert_string_into_datetime(str_max_day_checkin)
        # print("New values after UTC====CHECKIN=====>>>>",min_day_checkin,max_day_checkin)
        # min_day_checkout = convert_string_into_datetime(str_min_day_checkout)
        # max_day_checkout = convert_string_into_datetime(str_max_day_checkout)
        # print("New values after UTC====CHECKIN=====>>>>", min_day_checkout, max_day_checkout)
        #
        # expected_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(record.hour_from * 60, 60))
        # expected_checkin_sting_date = convert_string_into_datetime(str(record.date) + ' ' + expected_time + ':00')
        # expected_checkin = datetime.strptime(expected_checkin_sting_date, '%Y-%m-%d %H:%M:%S')
        # expected_time2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(record.hour_to * 60, 60))
        # expected_checkout_sting_date = convert_string_into_datetime(str(record.date) + ' ' + expected_time2 + ':00')
        # expected_checkout = datetime.strptime(expected_checkout_sting_date, '%Y-%m-%d %H:%M:%S')

        # print("=======DAY CHECKIN========", str_min_day_checkin, str_max_day_checkin,str_min_day_checkout,str_max_day_checkout)
