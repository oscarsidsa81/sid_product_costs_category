# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sid_cost_category = fields.Monetary(
        string='Coste Recomendado',
        related='product_id.sid_cost_category',
        store=True,
        currency_field='currency_id',
        readonly=True,
    )
