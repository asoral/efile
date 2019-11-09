from odoo import api, fields, models, _

class IRModel(models.Model):
    _inherit = "ir.model"


    def get_current_object_check_branch(self,model):
       for s in self:
           model = self.env[model].get_fields()
           print("modle idddddddddddddddd".model)
           if model.branch_id:
               return True