# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sid_currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )
    sid_cost_avg_ton = fields.Monetary(
        string='Coste Prom. de Productos',
        currency_field='sid_currency_id',
    )
    sid_cost_ton = fields.Monetary(
        string='Coste Categoría',
        currency_field='sid_currency_id',
    )
    sid_cost_ref_date = fields.Date(
        string='Fecha Ref. Coste',
        compute='_compute_sid_cost_ref_date',
    )

    @api.depends('create_uid')
    def _compute_sid_cost_ref_date(self):
        today = fields.Date.context_today(self)
        ref_date = today - timedelta(days=180)
        for rec in self:
            rec.sid_cost_ref_date = ref_date
