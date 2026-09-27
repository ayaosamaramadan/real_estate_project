from odoo import api, models
from datetime import datetime, timedelta

class LeaseReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_lease_summary'
    _description = 'Lease Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data to report context
        """
        leases = self.env['real_estate.lease'].browse(docids)
        
     
        total_leases = len(leases)
        active_leases = len(leases.filtered(lambda lease: lease.state == 'active'))
        occupancy_rate = (active_leases / total_leases * 100) if total_leases else 0
      
        six_months_ago = datetime.now() - timedelta(days=180)
        maintenance_costs = {}
        property_payments = {}
        maintenance_requests = {}

        for lease in leases:
            costs = self.env['maintenance.request'].search([
                ('lease_id', '=', lease.id),
                ('completion_date', '>=', six_months_ago)
            ])
            maintenance_costs[lease.id] = sum(costs.mapped('actual_cost'))

            property_payments[lease.id] = lease.payment_ids.sorted(key='due_date')
           
            maintenance_requests[lease.id] = lease.main_ids.sorted(key='scheduled_date')
            
            
        return {
            'doc_ids': docids,
            'doc_model': 'real_estate.lease',
            'docs': leases,
            'occupancy_rate': occupancy_rate,
            'maintenance_costs': maintenance_costs,
            'property_payments': property_payments,
            'maintenance_requests': maintenance_requests,
            'report_date': datetime.now(),
            
        }
