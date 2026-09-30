from odoo import models, fields, api
from odoo.exceptions import AccessError


class Property(models.Model):
    # variables
    _name = 'real_estate.property'
    _description = 'Real Estate Property'
    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    area = fields.Float(string='Area (sq ft)')
    image_1920 = fields.Image(string='Property Image')
    available = fields.Boolean(string='Available', default=True, index=True)
    agent_id = fields.Many2one('res.users', string='sales person')
    lease_ids = fields.One2many(
        'real_estate.lease', 'property_id', string='Leases')
    payment_ids = fields.One2many(
        'lease.payment',
        'property_id',
        string='Payments',
    )
    created_date = fields.Datetime(
        string='Created Date', default=fields.Datetime.now, readonly=True)

    bathrooms = fields.Integer(string='Bathrooms', required=True)

    deposite = fields.Float(string='Deposite', required=False, default=0.0)
    lease_count = fields.Integer(
        string='Leases',
        compute='_compute_lease_count',
        store=True,
    )
    main_count = fields.Integer(
        string='Maintenance Requests',
        compute='_compute_main_count',
        store=True,
    )
    property_type = fields.Selection([
        ('vila', 'Villa'),
        ('apartment', 'Apartment'),
        ('office', 'Office'),
        ('house', 'House'),
        ('shop', 'Shop'),
        ('land', 'Land')
    ], required=True)
    
    external_id = fields.Char(string='External ID', index=True)

    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})

    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})

    def update_description(self):
        """Update the description for the property"""
        for record in self:
            record.write({'description': 'This is a beautiful property.'})

    def update_deposit(self):
        """Update the deposit amount for the property"""
        for record in self:
            record.write({'deposite': record.deposite + 1000})

    def add_bedroom(self):
        """Add a bedroom to the property"""
        for record in self:
            record.write({'bedrooms': record.bedrooms + 1})

    def prop_vila(self):
        """Change property type to 'vila' if available"""
        for record in self:
            if record.available:
                record.write({'property_type': 'vila'})

    def get_agent_name(self):
        """Write the name of the agent associated with the property to description"""
        for record in self:
            if record.agent_id:
                record.write({'description': record.agent_id.name})

    # on create if available ? edit bedrooms : error
    def create(self, vals):
        """Override the create method to set default values"""
        if not self.env.user.has_group('real_estate.group_property_manager'):
            vals['agent_id'] = self.env.user.id
        if 'available' not in vals:
            vals['available'] = True
        if 'bedrooms' not in vals:
            vals['bedrooms'] = 1
        return super(Property, self).create(vals)

    def write(self, vals):
        if not self.env.user.has_group('real_estate.group_property_manager'):
            if any(record.agent_id and record.agent_id != self.env.user for record in self):
                raise AccessError('You can only modify your own properties.')
            vals['agent_id'] = self.env.user.id
        return super(Property, self).write(vals)

    def view_leases(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'real_estate.action_lease'
        )
        action['domain'] = [('property_id', '=', self.id)]
        return action

    def view_main_requests(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'real_estate.action_maintenance_request'
        )
        action['domain'] = [('property_id', '=', self.id)]
        return action

    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)

    @api.depends('lease_ids.main_ids')
    def _compute_main_count(self):
        for record in self:
            record.main_count = len(record.lease_ids.mapped('main_ids'))

    def prop_summary(self):
        self.ensure_one()
        return self.env.ref('real_estate.action_report_property_summary').report_action(self)

    def export_excel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/real_estate/property/excel_export/{self.id}',
            'target': 'new',
        }
