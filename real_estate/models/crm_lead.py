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
        for record in self:
            record.write({'description': record.name})

    def action_open_create_tenant_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Tenant',
            'res_model': 'real_estate.tenant.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def _cron_create_tenants_from_leads(self):
        tenants = self.env['real_estate.tenant'].sudo()
        leads = self.search([('property_type', '!=', False)])

        for lead in leads:
            if tenants.search_count([('crm_id', '=', lead.id)]):
                continue

            tenants.create({
                'name': lead.contact_name or lead.partner_name or lead.name,
                'email': lead.email_from or 'no-email@example.com',
                'phone': lead.phone,
                'age_category': 'b',
                'notes': lead.property_type,
                'crm_id': lead.id,
            })

    def write(self, vals):
        vals = dict(vals)

        if 'expected_revenue' in vals:
            revenue = vals['expected_revenue']
            if revenue is not None and revenue <= 5000:
                raise UserError(
                    'Expected Revenue must be greater than 5000'
                )

        if 'name' in vals and 'description' not in vals:
            vals['description'] = vals['name']

        return super().write(vals)