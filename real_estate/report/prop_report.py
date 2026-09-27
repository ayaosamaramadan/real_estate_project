from odoo import api, models
from datetime import datetime, timedelta

class PropertyReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_property_summary'
    _description = 'Property Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data to report context
        """
        properties = self.env['real_estate.property'].browse(docids)
        
        # Calculate occupancy rate
        total_properties = len(properties)
        occupied = len(properties.filtered(lambda p: not p.available))
        occupancy_rate = (occupied / total_properties * 100) if total_properties > 0 else 0
        
        # Get maintenance costs for last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        maintenance_costs = {}
        property_payments = {}

        for prop in properties:
            costs = self.env['maintenance.request'].search([
                ('property_id', '=', prop.id),
                ('completion_date', '>=', six_months_ago)
            ])
            maintenance_costs[prop.id] = sum(costs.mapped('actual_cost'))

            payments = prop.lease_ids.mapped('payment_ids').sorted(key='due_date')
            property_payments[prop.id] = payments

        return {
            'doc_ids': docids,
            'doc_model': 'real_estate.property',
            'docs': properties,
            'occupancy_rate': occupancy_rate,
            'maintenance_costs': maintenance_costs,
            'property_payments': property_payments,
            'report_date': datetime.now(),
        }
