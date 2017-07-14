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
		pick_type = None
		for pt_id in picking_type_ids:
			picking_type = self.pool.get('stock.picking.type').browse(cr,uid,pt_id)
			if picking_type.default_location_src_id.usage == 'customer':
				picking_type_id = pt_id
				pick_type = picking_type
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
					'origin': order.name,
					'name': 'RET ' + order.name + ' - ' + line.product_id.name,
					'product_id': line.product_id.id,
					'product_uom': line.product_uom.id,
					'product_uom_qty': line.product_uom_qty * (-1),
					'location_id': picking_type.default_location_src_id.id,
					'location_dest_id': picking_type.default_location_dest_id.id,
					}
				return_lines.append(vals_line)
		if return_lines:
			return_picking_id = self.pool.get('stock.picking').create(cr,uid,vals_picking,context)
			vals_sale_order = {
				'return_picking_id': return_picking_id,
				}
			for return_line in return_lines:
				return_line['picking_id'] = return_picking_id
				move_id = self.pool.get('stock.move').create(cr,uid,return_line,context)
			return_id = self.pool.get('sale.order').write(cr,uid,ids[0],vals_sale_order,context)

			# Deletes stock moves with 0 qty
			for picking_id in order.picking_ids:
				move_ids = self.pool.get('stock.move').search(cr,uid,[('picking_id','=',picking_id.id)])
				for move_id in move_ids:
					stock_move = self.pool.get('stock.move').browse(cr,uid,move_id,context)
					if stock_move.product_uom_qty == 0:
						return_id = self.pool.get('stock.move').action_cancel(cr,uid,move_id,context)
        	return res

	def action_cancel(self, cr, uid, ids, context=None):
        	res = super(sale_order, self).action_cancel(cr,uid,ids,context)
		for order_id in ids:
			order = self.pool.get('sale.order').browse(cr,uid,order_id)
			if order.return_picking_id:
				return_picking = order.return_picking_id
				return_id = self.pool.get('stock.picking').action_cancel(cr,uid,[return_picking.id],context)
		return res


	def action_view_delivery(self, cr, uid, ids, context=None):
        	'''
	        This function returns an action that display existing delivery orders
        	of given sales order ids. It can either be a in a list or in a form
	        view, if there is only one delivery order to show.
        	'''

	        mod_obj = self.pool.get('ir.model.data')
        	act_obj = self.pool.get('ir.actions.act_window')

	        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree_all')
        	id = result and result[1] or False
	        result = act_obj.read(cr, uid, [id], context=context)[0]

        	#compute the number of delivery orders to display
	        pick_ids = []
        	for so in self.browse(cr, uid, ids, context=context):
	            pick_ids += [picking.id for picking in so.picking_ids]
		    if so.return_picking_id:
			pick_ids.append(so.return_picking_id.id)

        	#choose the view_mode accordingly
	        if len(pick_ids) > 1:
        	    result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
	        else:
        	    res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
	            result['views'] = [(res and res[1] or False, 'form')]
        	    result['res_id'] = pick_ids and pick_ids[0] or False
	        return result



sale_order()
