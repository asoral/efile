from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # buffer_time_float = fields.Float(string="Buffer Time",help="This field helps to Add the Buffer Time In Login",config_parameter='currated_attendance.buffer_time_float')

    source_attendance_data_from = fields.Selection([
                                                    ('attendance', 'Attendance'),
                                                    ('raw_data', 'Raw data'),],
                                                    string='Source Attendance Data from',config_parameter='currated_attendance.source_attendance_data_from',default='attendance')