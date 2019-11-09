# -*- coding: utf-8 -*-
# Developer:Pavan Panchal
from odoo import models, fields, api, _


class VisitorUser(models.Model):
    """
        For Visitor,
        This model is Registry log.
        Like,When we visit any office there's visitor card will be given for visit the office
    """
    _name = 'visitor.log'
    _order = "visitor_log desc"
    _rec_name = "visitor_id"
    _description = "Visitor Register"

    visitor_id = fields.Char(string='Visitor Bio-ID', readonly=True,
                             help="Visitor biometric  ID")
    visitor_log = fields.Datetime(string='Entry Log', readonly=True,
                                  help="Entry log is datetime")
    visitor_device = fields.Many2one(
        "bio.server", string="Biometric Device")


class BioRowData(models.Model):
    _name = 'row.data'
    _order = "row_date_time desc"
    _rec_name = "row_bio_id"
    _description = "Biometric Row data"

    row_emp_name = fields.Many2one(
        "hr.employee", string="Employee", compute='_compute_row_device', store=True)
    row_bio_id = fields.Char(string='Biometric ID')
    row_date_time = fields.Datetime(string='Datetime')
    row_device = fields.Many2one(
        "bio.server", string="Biometric Device")

    @api.depends('row_bio_id')
    def _compute_row_device(self):
        for recs in self:
            if recs.row_bio_id:
                emp_id = self.env["hr.employee"].search(
                    [('bioid', '=', recs.row_bio_id)], limit=1)
                if emp_id:
                    recs.row_emp_name = emp_id.id
