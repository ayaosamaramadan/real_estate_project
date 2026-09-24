from odoo import models, fields, api, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_normalize

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

    def action_create_portal_user(self):
        """Create a portal account for this tenant and link it automatically."""
        self.ensure_one()
        if self.user_id:
            raise UserError('This tenant is already linked to a user.')

        email = email_normalize(self.email)
        if not email:
            raise ValidationError('A valid email address is required to create a portal user.')

        users = self.env['res.users'].sudo().with_context(active_test=False)
        existing_user = users.search([('login', '=ilike', email)], limit=1)
        if existing_user:
            if not existing_user.has_group('base.group_portal'):
                group_internal = self.env.ref('base.group_user')
                group_portal = self.env.ref('base.group_portal')
                group_public = self.env.ref('base.group_public')
                existing_user.write({
                    'active': True,
                    'groups_id': [
                        Command.unlink(group_internal.id),
                        Command.link(group_portal.id),
                        Command.unlink(group_public.id),
                    ],
                })
                wizard = self.env['portal.wizard'].with_context(
                    default_partner_ids=[existing_user.partner_id.id],
                ).create({
                    'partner_ids': [Command.set(existing_user.partner_id.ids)],
                })
                wizard_user = wizard.user_ids.filtered(
                    lambda item: item.partner_id == existing_user.partner_id
                )[:1]
                wizard_user.action_invite_again()
            elif not existing_user.active:
                existing_user.write({'active': True})
            self.user_id = existing_user
            return True

        partner = self.env['res.partner'].sudo().search([
            ('email', '=ilike', email),
        ], limit=1)
        if not partner:
            partner = self.env['res.partner'].sudo().create({
                'name': self.name,
                'email': email,
                'phone': self.phone,
                'mobile': self.mobile,
            })

        wizard = self.env['portal.wizard'].with_context(
            default_partner_ids=[partner.id],
        ).create({
            'partner_ids': [Command.set(partner.ids)],
        })
        wizard_user = wizard.user_ids.filtered(
            lambda item: item.partner_id == partner
        )[:1]
        wizard_user.action_grant_access()
        self.user_id = wizard_user.user_id
        return True

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
