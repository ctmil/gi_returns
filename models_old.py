# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv,fields
from openerp import models, api, tools
from openerp.exceptions import Warning
from datetime import date

class sale_order(osv.osv):
	_inherit = 'sale.order'

	_columns = {
		'return_picking_id': fields.many2one('stock.picking','Mov de Retorno'),
		'refund_id': fields.many2one('account.invoice','NC de Retorno'),
		}

	def action_button_confirm(self, cr, uid, ids, context=None):
        	res = super(sale_order, self).action_button_confirm(cr,uid,ids,context)
		order = self.pool.get('sale.order').browse(cr,uid,ids[0])
		picking_type_id = None
		picking_type_ids = self.pool.get('stock.picking.type').search(cr,uid,[('code','=','incoming'),('warehouse_id','=',order.warehouse_id.id)])
		for pt_id in picking_type_ids:
			picking_type = self.pool.get('stock.picking.type').browse(cr,uid,pt_id)
			if picking_type.default_location_src_id.usage == 'customer':
				picking_type_id = pt_id
		if not picking_type_id:
			raise Warning('No hay movimiento de devolucion definido')
		vals_picking = {
			'name': 'RET ' + order.name,
			'partner_id': order.partner_id.id,
			'date': str(date.today()),
			'origin': order.name,
			'move_type': 'one',
			'picking_type_id': picking_type_id,
			}
		return_lines = []
		for line in order.order_line:
			if line.product_uom_qty < 0:
				vals_line = {
					'product_id': line.product_id.id,
					'product_uom': line.product_uom.id,
					'product_uom_qty': line.product_uom_qty
					}
				return_lines.append(vals_line)
		if return_lines:
			return_picking_id = self.pool.get('stock.picking').create(cr,uid,vals_picking,context)
			vals_sale_order = {
				'return_picking_id': return_picking_id
				}
			return_id = self.pool.get('sale.order').write(cr,uid,ids[0],vals_sale_order,context)
        	return res

sale_order()
