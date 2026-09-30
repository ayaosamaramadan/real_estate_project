import odoo
from odoo import http, fields
from odoo.http import request
import json
from functools import wraps


class RealEstateAPI(http.Controller):

    @http.route('/api/properties/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        try:
            params = kwargs
            print(request.env.user.name)
            # if not request.env.user.has_group('real_estate.group_property_manager'):
            #     return {
            #         'status': 'error',
            #         'message': 'You do not have permission to create properties'
            #     }

            # Validate required fields
            if not params.get('name') or not params.get('price'):
                return {
                    'status': 'error',
                    'message': 'Name and price are required'
                }

            # Create property
            property_obj = request.env['real_estate.property'].sudo().create({
                'name': params.get('name'),
                'price': params.get('price'),
                'bedrooms': params.get('bedrooms', 0),
                'property_type': params.get('property_type', 'house'),
                'external_id': params.get('external_id'),
            })

            return {
                'status': 'success',
                'message': 'Property created successfully',
                'data': {
                    'property_id': property_obj.id,
                    'name': property_obj.name,
                    'external_id': property_obj.external_id
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/tenants/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_tenant(self, **kwargs):
        try:
            params = kwargs
            if not params.get('name') or not params.get('email'):
                return {
                    'status': 'error',
                    'message': 'Name and email are required'
                }

            tenant = request.env['real_estate.tenant'].sudo().create({
                'name': params['name'],
                'email': params['email'],
                'created_from_api': True,
            })

            return {
                'status': 'success',
                'message': 'Tenant created successfully',
                'data': {
                    'tenant_id': tenant.id,
                    'name': tenant.name,
                    'email': tenant.email,

                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    
    @http.route('/api/tenants/<int:tenant_id>', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_phone_tenant(self, tenant_id, **kwargs):
        try:
            params = kwargs
            tenant = request.env['real_estate.tenant'].sudo().browse(tenant_id)
            if not tenant.exists():
                return {
                    'status': 'error',
                    'message': 'Tenant not found'
                }

            if not tenant.active:
                return {
                    'status': 'error',
                    'message': 'Tenant is inactive; phone was not updated'
                }

            if 'phone' in params:
                tenant.write({'phone': params['phone']})

            return {
                'status': 'success',
                'message': 'Tenant updated successfully',
                'data': {
                    'tenant_id': tenant.id,
                    'name': tenant.name,
                    'phone': tenant.phone,
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }