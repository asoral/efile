from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Advice(models.Model):
    _inherit = "hr.payroll.advice"

    journal_id = fields.Many2one('account.journal', 'Journal')

    @api.onchange('journal_id')
    def compute_bank(self):
        # for rec in self:
        if self.journal_id and self.journal_id.bank_id:
            self.bank_id = self.journal_id.bank_id.id

    @api.onchange('journal_id')
    def compute_journals_domain(self):
        record = self.env['account.journal'].search([('type', 'in', ['cash', 'bank'])])
        return {
            'domain': {
                'journal_id': [('id', 'in', record.ids)]
            }}

    @api.multi
    def confirm_sheet(self):
        res = super(Advice, self).confirm_sheet()
        total = sum([line.bysal for line in self.line_ids])
        line_ids = []
        for line in self.line_ids:
            line_ids.append((0, 0, dict(
                name='debit',
                debit=line.bysal,
                account_id=self.env.ref('hr_payroll.hr_rule_net').account_debit.id,
                partner_id=line.employee_id.address_home_id.id,
            )))
        line_ids.append((0, 0, dict(
            name=self.number,
            credit=total,
            account_id=self.journal_id.default_credit_account_id.id,
            # partner_id=line.employee_id.address_home_id.id,
        )))
        move_id = self.env['account.move'].create(dict(
            name='/',
            date=str(datetime.now().date()),
            journal_id=self.journal_id.id,
            line_ids=line_ids,
        ))
        move_id.post()
        return res