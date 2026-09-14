from odoo import models, fields, api

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    crm_id = fields.Many2one('crm.lead', string='CRM Lead')
            
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True) 
    
    
    def update_notes(self):
        """Update the notes for the tenant"""
        for record in self:
            record.write({'notes': record.name})

    def get_lead_name(self):
            for record in self:
                record.write({'notes': record.crm_id.website})

    def get_lead_email(self):
            for record in self:
                notes = record.crm_id.website or record.crm_id.email_from
                record.write({'notes': notes})
    