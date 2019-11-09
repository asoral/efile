from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Applicant(models.Model):
    _inherit = "hr.applicant"

    date_of_birth = fields.Date('Date Of Birth')
    place_of_birth = fields.Char('Place Of Birth')

class SelectTraining(models.TransientModel):

    _inherit = 'select.training'

    @api.multi
    def action_done(self):
        res = super(SelectTraining, self).action_done()
        applicant_id = self.env['hr.applicant'].search([('id', '=', self._context.get('active_id'))])
        applicant_id.emp_id.birthday = applicant_id.date_of_birth
        return res

class ApplicantPreviousOccupation(models.Model):
    _inherit = "applicant.previous.occupation"

    reasons = fields.Text('Reasons')
