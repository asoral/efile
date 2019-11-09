# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class DeletAttendanceWizard(models.TransientModel):
    _name = 'delet.attendance.wizard'
    _description ="Delete attendance wizard"

    @api.multi
    def delete_all_attendances(self):
        if self._context and self._context.get('active_ids'):
            for active_rec in self._context.get('active_ids'):
                rec = self.env['bio.server'].browse(active_rec)
                rec.delete_all_attendance()
