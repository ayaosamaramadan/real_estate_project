from odoo import models, fields, api

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'
    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)    
    agent_id = fields.Many2one('res.users', string='sales person')
    deposite = fields.Float(string='Deposite', required=True)
   
    property_type = fields.Selection([
            ('vila', 'Villa'),
            ('apartment', 'Apartment'),
            ('office', 'Office'),
            ('shop', 'Shop'),
            ('land', 'Land')
        ], required=True)


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
           