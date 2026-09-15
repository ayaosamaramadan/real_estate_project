from odoo import models, fields
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)

    def update_description(self):
        """Update the description for the lead"""
        for record in self:
            record.write({'description': record.name})
            
    def write(self, vals):        
              if 'active' in vals and vals['active'] == True:
                  print("name:", vals.get('name'))
              vals['description'] = vals.get('name')
              if vals.get('expected_revenue') > 5000:
                  vals['description'] = f"Expected Revenue: {vals['expected_revenue']}"
              else:
                  raise UserError("Expected Revenue must be greater than 5000")
              vals['description'] = self.name
              return super(CrmLead, self).write(vals)