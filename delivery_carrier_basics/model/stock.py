# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Digital5 S.L.
#                  Jon Erik Ceberio <jonerikceberio@digital5.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    @api.depends('move_lines.product_qty', 'move_lines')
    def _amount_all(self):
        amount_untaxed = 0.0
        amount_tax = 0.0
        amount_assured = 0.0
        for move in self.move_lines:
            line = move.procurement_id and move.procurement_id.sale_line_id or False
            if line:
                price = line._calc_line_base_price(line)
                qty = move.product_qty
                taxes = line.tax_id.compute_all(price, qty,
                                        line.product_id,
                                        line.order_id.partner_id)
                cur = line.order_id.pricelist_id.currency_id
                amount_untaxed += cur.round(taxes['total'])
                for tax in taxes['taxes']:
                    amount_tax += cur.round(tax.get('amount', 0.0))
                amount_assured += cur.round(line.assured_amount * qty)
        self.amount_untaxed = amount_untaxed
        self.amount_tax = amount_tax
        self.amount_total = amount_untaxed + amount_tax
        self.amount_assured = amount_assured

    amount_untaxed = fields.Float(string='Untaxed Amount', digits=dp.get_precision('Account'), readonly=True, compute='_amount_all')
    amount_tax = fields.Float(string='Taxes', digits=dp.get_precision('Account'), readonly=True, compute='_amount_all')
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'), readonly=True, compute='_amount_all')
    amount_assured = fields.Float(string='Assured Total', digits=dp.get_precision('Account'), readonly=True, compute='_amount_all')
