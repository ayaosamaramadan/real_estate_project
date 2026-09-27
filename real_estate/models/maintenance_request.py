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

    @api.model
    def cron_daily_maintenance_reminder(self):
        """Send a daily reminder to the assigned user with client and apartment information."""
        today = fields.Date.today()
        records = self.search([
            ('scheduled_date', '=', today),
            ('assigned_to', '!=', False),
        ])

        for record in records:
            user = record.assigned_to
            if not user or not user.partner_id.email:
                continue

            client_name = record.tenant_id.name or 'Client'
            apartment_name = record.property_id.name or 'Apartment'
            issue_name = dict(record._fields['issue_type'].selection).get(record.issue_type, record.issue_type or 'Maintenance')

            body_html = f"""
                <div style="font-family: Arial, sans-serif; font-size: 14px;">
                    <p>Hello {user.name},</p>
                    <p>This is a reminder for the client <b>{client_name}</b> in apartment <b>{apartment_name}</b>.</p>
                    <p><b>Issue:</b> {issue_name}<br/>
                    <b>Scheduled date:</b> {record.scheduled_date}</p>
                </div>
            """

            mail = self.env['mail.mail'].sudo().create({
                'subject': f'Reminder: {client_name} - {apartment_name}',
                'body_html': body_html,
                'email_from': self.env.user.email_formatted or self.env.company.email or 'noreply@example.com',
                'email_to': user.partner_id.email,
                'auto_delete': True,
            })
            mail.send()

        return True

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