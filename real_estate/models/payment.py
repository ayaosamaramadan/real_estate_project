from odoo import models, fields, api
# from odoo.exceptions import UserError
# from datetime import timedelta

class LeasePayment(models.Model):
    _name = 'lease.payment'
    _description = 'Lease Payment'
    _order = 'due_date desc, id desc'

    name = fields.Char(string='Payment Reference', required=True, copy=False, readonly=True, default='New')
    lease_id = fields.Many2one('real_estate.lease', string='Lease', required=True, ondelete='cascade')
    tenant_id = fields.Many2one('real_estate.tenant', related='lease_id.tenant_id', string='Tenant', store=True)
    property_id = fields.Many2one('real_estate.property', string='Property', tracking=True)

    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    amount = fields.Float(string='Amount Due', required=True, tracking=True)
    late_fee = fields.Float(string='Late Fee', tracking=True)
    late_fee_applied = fields.Boolean(string='Late Fee Applied', default=False)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled')
    ], default='draft', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'lease.payment'
                ) or 'New'

            lease_id = vals.get('lease_id')
            if lease_id and not vals.get('property_id'):
                lease = self.env['real_estate.lease'].browse(lease_id)
                vals['property_id'] = lease.property_id.id if lease.property_id else False

        return super().create(vals_list)

    @api.onchange('lease_id')
    def _onchange_lease_id(self):
        if self.lease_id:
            self.property_id = self.lease_id.property_id
            self.tenant_id = self.lease_id.tenant_id

    @api.depends('amount', 'late_fee', 'late_fee_applied')
    def _compute_total_amount(self):
        for payment in self:
            payment.total_amount = payment.amount + (
                payment.late_fee if payment.late_fee_applied else 0.0
            )
    
            
    def _cron_auto_mark_payments_as_paid(self):
        """Scheduled action - mark payments as paid"""
        payments_to_update = self.search([
            ('state', '!=', 'paid'),  
            ('amount', '>', 0.0), 
        ])
        payments_to_update.write({'state': 'paid'})