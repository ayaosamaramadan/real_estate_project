from odoo import models, fields, api
from odoo.exceptions import UserError


class Lease(models.Model):


    # variables
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    
    name = fields.Char(string='Lease Reference', required=True, readonly=True, default='New')
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade', 
        index=True
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('at_risk', 'At Risk'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ], string='Status', default='draft', required=True)
    
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    main_ids = fields.One2many(
        'maintenance.request',
        'lease_id',
        string='Maintenance Requests'
    )
    
    duration_month = fields.Integer(string='Duration (Months)', compute='_compute_duration' ,store=True)
    
    comp_is_active = fields.Boolean(string='Is Active', compute='_compute_is_active', store=False)
      
           
    # make on create to generate lease reference with sequence number
    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('real_estate.lease')
                or 'New'
            )
        return super(Lease, self).create(vals)

    # make on duplicate to generate new lease reference with sequence number
    # def copy(self, default=None):
    #     raise UserError('You cannot duplicate a lease.')
    
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease') or 'New'
        return super(Lease, self).copy(default)
   
    def update_to_active(self):
        self.write({'state': 'active'})

    def update_to_draft(self):
        self.write({'state': 'draft'})
        
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_month = delta.days // 30
            else:
                record.duration_month = 0
                
    @api.depends('start_date', 'end_date' , 'state')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.comp_is_active = record.start_date <= today <= record.end_date
            else:
                record.comp_is_active = False