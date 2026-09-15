from odoo import models, fields

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
