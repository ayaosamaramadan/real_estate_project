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
