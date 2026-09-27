from datetime import timedelta

from odoo import models, fields, api


class ResPar(models.Model):
    _inherit = 'res.partner'

    specialization = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ], string='Specialization')

    @api.model
    def cron_send_reminder(self):
        """Legacy compatibility hook. The active reminder cron is on maintenance.request."""
        return True
