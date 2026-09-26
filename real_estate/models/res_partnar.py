from odoo import models, fields


class ResPar(models.Model):
    _inherit = 'res.partner'

    specialization = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ], string='Specialization')
