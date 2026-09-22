from datetime import timedelta
from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Property Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char()
    lease_id = fields.Many2one('real_estate.lease', string='Lease')
    tenant_id = fields.Many2one(
        related='lease_id.tenant_id',
        store=True,
        string='Tenant',
    )
    property_id = fields.Many2one(
        related='lease_id.property_id',
        store=True,
        string='Property',
    )
    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], required=True)
    description = fields.Text(required=True, tracking=True)
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], default='medium', required=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    scheduled_date = fields.Date()
    completion_date = fields.Date()
    actual_cost = fields.Float(string='Actual Cost')

    @api.model_create_multi
    def create(self, vals_list):
        tomorrow = fields.Date.today() + timedelta(days=1)

        for vals in vals_list:
            if vals.get('urgency') == 'emergency' and not vals.get('scheduled_date'):
                vals['scheduled_date'] = tomorrow

        return super().create(vals_list)

    @api.onchange('urgency')
    def _onchange_urgency(self):
        if self.urgency == 'emergency':
            self.scheduled_date = fields.Date.today() + timedelta(days=1)