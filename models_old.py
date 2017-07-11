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

class sale_order(osv.osv):
	_inherit = 'sale.order'

	_columns = {
		'return_picking_id': fields.many2one('stock.picking','Mov de Retorno'),
		'refund_id': fields.many2one('account.invoice','NC de Retorno'),
		}

	def action_button_confirm(self, cr, uid, ids, context=None):
        	res = super(sale_order, self).action_button_confirm(cr,uid,ids,context)
		order = self.pool.get('sale.order').browse(cr,uid,ids[0])
		for line in order.order_line:
			if line.product_uom_qty < 0:
				import pdb;pdb.set_trace()
        	return res

sale_order()
