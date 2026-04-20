# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sid_cost_category = fields.Monetary(
        string='Coste Unit. Categoría',
        compute='_compute_sid_cost_category',
        store=True,
        currency_field='currency_id',
        readonly=True,
    )
    sid_cost_ton_category = fields.Monetary(
        string='Precio Ton Categoría',
        related='categ_id.sid_cost_ton',
        store=True,
        currency_field='currency_id',
        readonly=True,
    )
    sid_cost_ref_date = fields.Date(
        string='Fecha Ref. Coste',
        related='categ_id.sid_cost_ref_date',
        readonly=True,
    )

    @api.depends('categ_id.sid_cost_ton', 'weight')
    def _compute_sid_cost_category(self):
        for rec in self:
            if rec.categ_id and rec.weight:
                rec.sid_cost_category = (rec.categ_id.sid_cost_ton * rec.weight) / 1000.0
            else:
                rec.sid_cost_category = 0.0
