from odoo import models, api, fields,_
from odoo.exceptions import ValidationError

class AddFiles(models.Model):
    _inherit = "muk_dms.directory"
    _description = "Add Files"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.id == self.env.ref('smart_office.smart_office_directory').id or \
                    rec.id == self.env.ref('smart_office.smart_office_directory_root').id:
                raise ValidationError(_('\"Incoming Files\" and \"Root Directory\" directory cannot be deleted!'))
        return super(AddFiles, self).unlink()

    doc_file_date = fields.Date('File Date', default=fields.Date.context_today)
    doc_type_of_file = fields.Text('Type of File')
    doc_file_status = fields.Selection([('normal', 'Normal'),
                                        ('important', 'Important'),
                                        ('urgent', 'Urgent')], default='normal')
    doc_subject_matter = fields.Text('Subject Matter')

    @api.model
    def create(self, vals):
        if self._context.get('smart_office', False):
            vals['parent_directory'] = self.env.ref('smart_office.smart_office_directory_root').id
            vals['inherit_groups'] = True
        return super(AddFiles, self).create(vals)

    doc_file_preview = fields.Binary()

    def save_record(self):
        self.doc_file_preview = self.files[0].content
        return {
            'name': 'Incoming Files',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {'tree_view_ref': 'smart_office.view_add_files_incoming_tree'},
        }
        pass

    def deal_with_file(self):
        return {
            'name': 'Files',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'muk_dms.directory',
            'type': 'ir.actions.act_window',
            # 'target': 'main',
            'res_id': self.id,
            'context': {'form_view_ref': 'smart_office.view_add_files_doc_form_incoming'},
        }
        pass

    note_log_ids = fields.One2many('muk.note.log', 'file_id')

    # action group
    file_action = fields.Selection([('forward', 'Forward'),
                                    ('closed', 'Closed')], default='forward')
    designation_id = fields.Many2one('muk.designation', 'Designation')
    doc_remarks = fields.Text('Remarks')
    # doc_name = fields.Many2one('muk_dms.directory', 'Name')

    @api.onchange('doc_name')
    def compute_doc_name_details(self):
        pass

class NoteLog(models.Model):
    _name = "muk.note.log"

    name = fields.Html('Note: ')
    file_id = fields.Many2one('muk_dms.directory')

class Designation(models.Model):
    _name = "muk.designation"

    name = fields.Char('Name')