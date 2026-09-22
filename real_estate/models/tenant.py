from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
    user_id = fields.Many2one('res.users', string='Related User', index=True)

    age_category = fields.Selection([
            ('a', '1-20'),
            ('b', '21-40'),
            ('c', '41-60'),
            ], required=True)
            
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True) 
    lease_ids = fields.One2many('real_estate.lease', 'tenant_id', string='Leases')
    
    age_tenant = fields.Integer(string='Age', compute='_compute_age', store=True)
       
    
    
    def update_notes(self):
        """Update the notes for the tenant"""
        for record in self:
            record.write({'notes': record.name})

    def get_lead_name(self):
         for record in self:
              record.write({'notes': record.crm_id.name})

    def get_lead_email(self):
            for record in self:
                notes = record.crm_id.website or record.crm_id.email_from
                record.write({'notes': notes})
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                age = today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
                record.age_tenant = age
            else:
                record.age_tenant = 0

    @api.constrains('date_of_birth')
    def _check_minimum_age(self):
        for record in self:
            if record.date_of_birth and record.age_tenant < 20:
                raise ValidationError('Tenant age must be at least 20 years.')