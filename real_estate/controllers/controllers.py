# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from werkzeug.exceptions import NotFound


class RealEstatePortal(CustomerPortal):

	def _prepare_portal_layout_values(self):
		values = super()._prepare_portal_layout_values()
		tenant = request.env['real_estate.tenant'].sudo().search([
			('user_id', '=', request.env.user.id),
		], limit=1)
		lease_count = 0
		if tenant:
			lease_count = request.env['real_estate.lease'].sudo().search_count([
				('tenant_id', '=', tenant.id),
			])
		values.update({
			'lease_count': lease_count,
			'tenant': tenant,
		})
		return values

	@http.route(
		['/my/leases', '/my/leases/page/<int:page>'],
		type='http',
		auth='user',
		website=True,
	)
	def portal_my_leases(self, page=1, **kw):
		values = self._prepare_portal_layout_values()
		tenant = values.get('tenant')
		leases = request.env['real_estate.lease'].sudo().browse()
		if tenant:
			leases = request.env['real_estate.lease'].sudo().search([
				('tenant_id', '=', tenant.id),
			], order='start_date desc')
		values.update({'leases': leases})
		return request.render('real_estate.portal_my_leases', values)

	@http.route(
		'/property/<int:property_id>/<string:slug>',
		type='http',
		auth='user',
		website=True,
	)
	def portal_property_details(self, property_id, slug=None, **kw):
		"""Show a property only to the portal user leasing it."""
		tenant = request.env['real_estate.tenant'].sudo().search([
			('user_id', '=', request.env.user.id),
		], limit=1)
		lease = request.env['real_estate.lease'].sudo().search([
			('tenant_id', '=', tenant.id),
			('property_id', '=', property_id),
		], limit=1)
		if not lease:
			raise NotFound()

		values = self._prepare_portal_layout_values()
		values.update({
			'property_record': lease.property_id,
			'lease': lease,
		})
		return request.render('real_estate.portal_property_details', values)

	@http.route('/properties', type='http', auth='public', website=True)
	def website_properties(self, property_type=None, min_price=None,
						   max_price=None, bedrooms=None, **kw):
		"""Public property catalogue with URL-based filters."""
		property_model = request.env['real_estate.property'].sudo()
		property_types = property_model._fields['property_type'].selection
		valid_property_types = {value for value, _label in property_types}
		domain = [('available', '=', True)]

		if property_type in valid_property_types:
			domain.append(('property_type', '=', property_type))
		else:
			property_type = False

		try:
			min_price = float(min_price) if min_price else False
		except (TypeError, ValueError):
			min_price = False
		if min_price is not False:
			domain.append(('price', '>=', min_price))

		try:
			max_price = float(max_price) if max_price else False
		except (TypeError, ValueError):
			max_price = False
		if max_price is not False:
			domain.append(('price', '<=', max_price))

		try:
			bedrooms = int(bedrooms) if bedrooms else False
		except (TypeError, ValueError):
			bedrooms = False
		if bedrooms is not False:
			domain.append(('bedrooms', '>=', bedrooms))

		return request.render('real_estate.website_properties', {
			'properties': property_model.search(domain, order='price asc'),
			'property_types': property_types,
			'property_types_map': dict(property_types),
			'selected_type': property_type,
			'min_price': min_price,
			'max_price': max_price,
			'bedrooms': bedrooms,
		})

	@http.route('/properties/<int:property_id>', type='http', auth='public', website=True)
	def website_property_details(self, property_id, **kw):
		"""Public details page for an available property."""
		property_record = request.env['real_estate.property'].sudo().browse(property_id)
		if not property_record.exists() or not property_record.available:
			raise NotFound()
		return request.render('real_estate.website_property_details', {
			'property_record': property_record,
			'property_types_map': dict(
				property_record._fields['property_type'].selection,
			),
		})
