from odoo import api, fields, models, _

class BaseBranch(models.Model):
    _inherit = "res.branch"


    report_header = fields.Text(string='Company Tagline', help="Appears by default on the top right corner of your printed documents (report header).")
    report_footer = fields.Text(string='Report Footer', translate=True, help="Footer text displayed at the bottom of all reports.")
    external_report_layout_id = fields.Many2one('ir.ui.view', 'Document Template')