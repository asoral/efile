from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions
import logging
_logger = logging.getLogger(__name__)



class HrAttendanceRoaster(models.Model):
    _name = 'hr.overtime.request'
    _description = "Employee Overtime Request"

    employee_id = fields.Many2one('hr.employee',string="Employee")
    date = fields.Date(string="Date")
    overtime_hours = fields.Float(string="Overtime Hours")
    shift_id = fields.Many2one('resource.calendar',string="Shift Name")
    shift_line_id = fields.Many2one('resource.calendar.attendance',string="Shift Line")
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
