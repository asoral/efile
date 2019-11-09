# -*- coding: utf-8 -*-
# Developer:Pavan Panchal
import pytz
import logging
import datetime
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from . import zkteco

_logger = logging.getLogger(__name__)


@api.model
def _tz_get(self):
    return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz
                                      if not tz.startswith('Etc/') else '_')]


class bio_config(models.Model):
    """
     To the Biometric Server configuration
    """
    _name = "bio.server"
    _description = "Biometric Server Configuration"
    _rec_name = "name"

    name = fields.Char(string="Name", translate=True, help="Add device name")
    bioip = fields.Char(string="Biometric IP address", translate=True,
                        help="Add biometric IP address")
    bioport = fields.Char(
        string="Biometric Port",
        default=4370,
        translate=True,
        help="Add biometric port")
    bio_tz = fields.Selection(_tz_get, string="Biometric Timezone",
                              default="Asia/Calcutta",
                              help="Add biometric device timezone")

    @api.constrains('bioport', 'bioip')
    def _check_biometric(self):
        """
        Validation Constrains on the IP & PORT of Biometric Device
        """
        for ids in self:
            if ids.bioport:
                bio_port = ids.bioport
                if bio_port.isdigit():
                    if (len(bio_port) > 4) or (len(bio_port) < 2):
                        raise exceptions.ValidationError(
                            _('Biometric port length is should not be less \
                                than 2 and not be greater then 4.'))
                else:
                    raise exceptions.ValidationError(
                        _('Biometric port must be in digit.'))
            if ids.bioip:
                bio_ip = ids.bioip
                if (len(bio_ip.split(".")) != 4):
                    raise exceptions.ValidationError(
                        _('Biometric ip length is should not be less than 4.'))
                else:
                    if len(bio_ip.split(".")) == 4:
                        for xips in bio_ip.split("."):
                            if xips.isdigit():
                                if (not len(xips)) or (len(xips) > 3):
                                    raise exceptions.ValidationError(
                                        _('Biometric ip digit length is should \
                                     not be  zero or not be greater than 3.'))
                            else:
                                raise exceptions.ValidationError(
                                    _('Biometric ip must be in the digit.'))

    @api.multi
    def fetch_row_data(self):
        """
         For the row data
        """
        for x in self.search([]):
            zk = zkteco.ZK(x.bioip,
                           int(x.bioport),
                           timeout=60,
                           password=0,
                           force_udp=False,
                           ommit_ping=False)
            conn = zk.connect()
            conn.enable_device()
            from datetime import datetime
            attendance_rec = conn.get_attendance()
            last_row_attn = self.env["row.data"].search([('row_device', '=', x.id)],
                                                        order='id desc', limit=1)
            last_row = last_row_attn.row_date_time
            for data in attendance_rec:
                local_dt_utc = (pytz.timezone(x.bio_tz).localize(
                    data.get('timestamp')).astimezone(pytz.utc).replace(tzinfo=None))
                if last_row:
                    if local_dt_utc > last_row:
                        self.env["row.data"].create(
                            {"row_bio_id": data.get('userid'),
                             "row_date_time": local_dt_utc,
                             "row_device": x.id})
                    else:
                        pass
                else:
                    self.env["row.data"].create(
                        {"row_bio_id": data.get('userid'),
                         "row_date_time": local_dt_utc,
                         "row_device": x.id})
        view = self.env.ref("zkteco_biometric.zkteco_action")
        return {
            'name': 'Row Attendance creation',
            'type': view.type,
            'res_model': view.res_model,
            'view_type': view.view_type,
            'view_mode': view.view_mode,
            'target': "new",
            'context': {"message": "Raw Attendances created"}}

    @api.multi
    def _cron_row_data(self):
        self.fetch_row_data()
        view = self.env.ref("zkteco_biometric.zkteco_action")
        return {
            'name': 'Row Attendance creation',
            'type': view.type,
            'res_model': view.res_model,
            'view_type': view.view_type,
            'view_mode': view.view_mode,
            'target': "new",
            'context': {"message": "Raw Attendances created"}}

    @api.multi
    def _cron_biometric(self):
        """
            Schedular Job
            From the biometric device Update Attendance into the Odoo Server.
        """
        """
            To get attedance row data using datetime sorted
        """
        from datetime import datetime

        for x in self.search([]):
            zk = zkteco.ZK(x.bioip, int(x.bioport), timeout=60, password=0,
                           force_udp=False, ommit_ping=False)
            conn = zk.connect()
            conn.enable_device()
            last_attn = self.env["hr.attendance"].search(['|', ('check_in_device', '=', x.id),
                                                          ('check_out_device', '=', x.id)],
                                                         order='id DESC', limit=1)
            last_attn_rec = last_attn.check_out or last_attn.check_in

            attendance_rec = conn.get_attendance()
            for data in attendance_rec:
                local_dt_utc = (pytz.timezone(x.bio_tz).localize(
                    data.get('timestamp')).astimezone(pytz.utc).replace(tzinfo=None))
                if last_attn_rec:
                    if local_dt_utc > last_attn_rec:
                        emp_rec = self.env['hr.employee'].search(
                            [('bioid', '=', data.get('userid'))], order='id DESC', limit=1)
                        if emp_rec:
                            emp_atten = self.env['hr.attendance'].search(
                                [('employee_id', '=', emp_rec.id)], order='id DESC', limit=1)
                            if emp_atten:
                                if not emp_atten.check_out:
                                    if local_dt_utc > emp_atten.check_in:
                                        emp_atten.write(
                                            {'check_out': local_dt_utc, 'check_out_device': x.id})
                                else:
                                    if local_dt_utc > emp_atten.check_out:
                                        dicts = {'employee_id': emp_rec.id,
                                                 'check_in': local_dt_utc,
                                                 'check_in_device': x.id}
                                        self.env['hr.attendance'].create(dicts)
                            else:
                                dicts = {'employee_id': emp_rec.id,
                                         'check_in': local_dt_utc,
                                         'check_in_device': x.id}
                                self.env['hr.attendance'].create(dicts)
                    else:
                        attendance = {'visitor_id': data.get('userid'),
                                      'visitor_log': local_dt_utc,
                                      'visitor_device': x.id
                                      }
                        self.env['visitor.log'].create(attendance)
                else:
                    emp_rec = self.env['hr.employee'].search(
                        [('bioid', '=', data.get('userid'))], order='id DESC', limit=1)
                    if emp_rec:
                        emp_atten = self.env['hr.attendance'].search(
                            [('employee_id', '=', emp_rec.id)], order='id DESC', limit=1)
                        if emp_atten:
                            if not emp_atten.check_out:
                                if local_dt_utc > emp_atten.check_in:
                                    emp_atten.write(
                                        {'check_out': local_dt_utc, 'check_out_device': x.id})
                            else:
                                if local_dt_utc > emp_atten.check_out:
                                    dicts = {'employee_id': emp_rec.id,
                                             'check_in': local_dt_utc,
                                             'check_in_device': x.id}
                                    self.env['hr.attendance'].create(dicts)
                        else:
                            dicts = {'employee_id': emp_rec.id,
                                     'check_in': local_dt_utc,
                                     'check_in_device': x.id}
                            self.env['hr.attendance'].create(dicts)
                    else:
                        attendance = {'visitor_id': data.get('userid'),
                                      'visitor_log': local_dt_utc,
                                      'visitor_device': x.id}
                        self.env['visitor.log'].create(attendance)
        view = self.env.ref("zkteco_biometric.zkteco_action")

        return {
            'name': 'Attendance creation',
            'type': view.type,
            'res_model': view.res_model,
            'view_type': view.view_type,
            'view_mode': view.view_mode,
            'target': "new",
            'context': {"message": "Attendance created"}}

    @api.multi
    def onclick_attendance(self):
        """
            On the click "Fetch attendance",
            to get attendance and update into Odoo server
        """
        self._cron_biometric()
        view = self.env.ref("zkteco_biometric.zkteco_action")
        return {
            'name': 'Attendance creation',
            'type': view.type,
            'res_model': view.res_model,
            'view_type': view.view_type,
            'view_mode': view.view_mode,
            'target': "new",
            'context': {"message": "Attendances created"}}

    @api.multi
    def generate_employees(self):
        """
            For using this method,
            Biometric device Users will be downloaded and converted as 
            Odoo as Employees.
        """
        emp_obj = self.env["hr.employee"]
        for recs in self:
            zk = zkteco.ZK(recs.bioip, int(recs.bioport), timeout=60,
                           password=0, force_udp=False, ommit_ping=False)
            conn = zk.connect()
            users = conn.get_users()
            if users:
                for user in users:
                    if not emp_obj.search([("bioid", "=", user.user_id) or
                                           ("name", "=", user.name)]):
                        emp_obj.create({"name": user.name,
                                        "bioid": user.user_id})
                view = self.env.ref("zkteco_biometric.zkteco_action")
                return {
                    'name': 'User creation',
                    'type': view.type,
                    'res_model': view.res_model,
                    'view_type': view.view_type,
                    'view_mode': view.view_mode,
                    'target': "new",
                    'context': {"message": "Get users successfully"}}
