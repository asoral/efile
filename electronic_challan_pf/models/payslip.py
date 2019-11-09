from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Reports(models.TransientModel):
    _name = "custom.payslip.reports"

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    # emp_tag_ids = fields.Many2many('hr.employee.category', 'source_dest_rel', 'source_id', 'dest_id', 'Employee Tags')
    x_pfcode1 = fields.Char('PF CODE')

    def get_report_data(self):
        self.env.cr.execute("""
            select hr_employee.name, hr_employee.id, hr_employee.x_uan1, 
            sum(CASE WHEN hr_payslip_line.code = 'GROSS' THEN hr_payslip_line.total ELSE 0 END ) GROSSTOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'EPFS' THEN hr_payslip_line.total ELSE 0 END ) EPFSTOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'PS' THEN hr_payslip_line.total ELSE 0 END ) PSTOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'PF' THEN hr_payslip_line.total ELSE 0 END ) PFTOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'EDLI' or hr_payslip_line.code = 'EDLI2' THEN hr_payslip_line.total ELSE 0 END ) EDLITOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'ESP' THEN hr_payslip_line.total ELSE 0 END ) ESPTOTAL,
            sum(CASE WHEN hr_payslip_line.code = 'EPF' THEN hr_payslip_line.total ELSE 0 END ) EPFTOTAL
            from employee_category_rel ,hr_employee, hr_payslip, hr_payslip_line where 
            employee_category_rel.emp_id=hr_employee.id and 
            hr_payslip.date_from>='%s' and 
            hr_payslip.date_to<='%s' and
            hr_payslip_line.slip_id=hr_payslip.id and 
            hr_payslip.employee_id=hr_employee.id and
            hr_payslip.employee_id=employee_category_rel.emp_id and
            hr_payslip.state='done' and 
            hr_employee.x_pfcode1='%s' 
            GROUP BY hr_employee.name, hr_employee.id;
        """ % (str(self.from_date), str(self.to_date), self.x_pfcode1))
        result = self.env.cr.dictfetchall()
        result = [{'pftotal': 0.0, 'name': 'Administrator', 'id': 1, 'epfstotal': 0.0, 'x_uan1': None, 'pstotal': 0.0, 'grosstotal': 20000.0, 'esptotal': 0.0, 'epftotal': 0.0, 'edlitotal': 0.0},
                  {'pftotal': 0.0, 'name': 'Administrator', 'id': 1, 'epfstotal': 0.0, 'x_uan1': None, 'pstotal': 0.0,
                   'grosstotal': 20000.0, 'esptotal': 0.0, 'epftotal': 0.0, 'edlitotal': 0.0}]
        return result

    def print_report(self):
        # hr.payslip.line
        return self.env['ir.actions.report']._get_report_from_name('electronic_challan_pf.label_contribution_register_view').report_action(self.id)