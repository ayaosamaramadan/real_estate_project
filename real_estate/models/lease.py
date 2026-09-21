from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Lease(models.Model):

    # variables
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'

    name = fields.Char(string='Lease Reference',
                       required=True, readonly=True, default='New')
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

    duration_month = fields.Integer(
        string='Duration (Months)', compute='_compute_duration', store=True)

    comp_is_active = fields.Boolean(
        string='Is Active', compute='_compute_is_active', store=False)

    next_elec_recharge = fields.Date(
        string='Next Electricity Recharge', compute='_onchange_start_date', store=False)

    total_actual_cost = fields.Float(
        string='Total Actual Cost', compute='_compute_total_actual_cost')
    # total_cost = fields.Float(compute='_compute_total_cost', string='Total Cost')
    
    
    
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
        default['name'] = self.env['ir.sequence'].next_by_code(
            'real_estate.lease') or 'New'
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

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.comp_is_active = record.start_date <= today <= record.end_date
            else:
                record.comp_is_active = False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Set default price when property is selected and validate availability"""
        if self.property_id and not self.property_id.available:
            raise ValidationError("The selected property is not available.")
        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price
            self.deposit_paid = self.property_id.price * 0.10

    @api.onchange('start_date')
    def _onchange_start_date(self):
        """Set next electricity recharge date based on start date"""
        if self.start_date:
            self.next_elec_recharge = self.start_date + timedelta(days=30)

    def create_maintenance_request(self):
        self.ensure_one()
        self.env['maintenance.request'].sudo().create({
            'lease_id': self.id,
            'issue_type': 'other',
            'description': 'Initial maintenance request',
            'scheduled_date': self.next_elec_recharge,
            'urgency': 'medium',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.depends('main_ids.actual_cost')
    def _compute_total_actual_cost(self):
        for record in self:
            total_cost = sum(
                request.actual_cost for request in record.main_ids)
            record.total_actual_cost = total_cost

    # @api.depends('maintenance_ids.actual_cost')
    # def _compute_total_cost(self):
    #     for lease in self:
    #         # 1
    #         # lease.total_cost = sum(maintenance.actual_cost for maintenance in lease.maintenance_ids)

    #         # 2
    #         # lease.total_cost = 0
    #         # total_cost = 0
    #         # for maintenance in lease.maintenance_ids:
    #         #     if maintenance.actual_cost:
    #         #         total_cost += maintenance.actual_cost
    #         # lease.total_cost = total_cost

    #         # 3
    #         lease_maintenance_ids = self.env['maintenance.request'].search([('lease_id', '=', lease.id)])
    #         lease.total_cost = 0
    #         for maintenance in lease_maintenance_ids:
    #             if maintenance.actual_cost:
    #                 lease.total_cost += maintenance.actual_cost
