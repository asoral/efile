# -*- coding: utf-8 -*-
# Developer:Pavan Panchal
from odoo import models, fields, _


class Employee(models.Model):
    """
        For employees,biometric ID
    """
    _inherit = "hr.employee"
    _description = "Employee"

    bioid = fields.Char(string="Biometric-ID",
                        help="Biometric id  of employee")

    _sql_constraints = [
        ('bioid_uniq',
         'unique (bioid)',
         "The Biometric ID must be unique, this one is \
         already assigned to another employee.")]


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_device = fields.Many2one(
        "bio.server", string="Check-in IP Address")
    check_out_device = fields.Many2one(
        "bio.server", string="Check-out IP Address")
