from odoo import fields, models


class TenantWizard(models.TransientModel):
    _name = 'real_estate.tenant.wizard'
    _description = 'Create Tenant Wizard'

    crm_id = fields.Many2one(
        'crm.lead',
        string='CRM Lead',
        required=True,
        readonly=True,
    )
    name = fields.Char(string='Tenant Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone Number')
    age_category = fields.Selection([
        ('a', '1-20'),
        ('b', '21-40'),
        ('c', '41-60'),
    ], string='Age Category', required=True)
    notes = fields.Text(string='Notes')

    def action_create_tenant(self):
        self.ensure_one()
        lead = self.env['real_estate.tenant'].sudo().create({
            'name': self.name,
            'phone': self.phone,
            'age_category': self.age_category,
            'notes': self.notes,
            'crm_id': self.crm_id.id,
            'email': self.email,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.tenant',
            'res_id': lead.id,
            'views': [(False, 'form')],
            'target': 'current',
        }
