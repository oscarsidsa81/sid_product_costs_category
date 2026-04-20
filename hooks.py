# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


COLUMN_RENAMES = {
    'product_category': {
        'x_avg_ton': 'sid_cost_avg_ton',
        'x_coste_ton': 'sid_cost_ton',
        'x_currency_id': 'sid_currency_id',
    },
    'product_template': {
        'x_coste_categoria': 'sid_cost_category',
        'x_precio_ton_categoria': 'sid_cost_ton_category',
    },
    'sale_order_line': {
        'x_studio_monetary_field_ExXXQ': 'sid_cost_category',
    },
}

FIELD_RENAMES = {
    ('product.category', 'x_avg_ton'): 'sid_cost_avg_ton',
    ('product.category', 'x_coste_ton'): 'sid_cost_ton',
    ('product.category', 'x_currency_id'): 'sid_currency_id',
    ('product.category', 'x_today'): 'sid_cost_ref_date',
    ('product.template', 'x_coste_categoria'): 'sid_cost_category',
    ('product.template', 'x_precio_ton_categoria'): 'sid_cost_ton_category',
    ('product.template', 'x_today'): 'sid_cost_ref_date',
    ('sale.order.line', 'x_studio_monetary_field_ExXXQ'): 'sid_cost_category',
}

STUDIO_VIEWS_TO_DISABLE = [
    ('product.category', 'Odoo Studio: product.category.form customization'),
    ('product.category', 'Odoo Studio: product.category.list customization'),
    ('product.template', 'Odoo Studio: product.template.product.form customization'),
]


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = %s
           AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())



def _rename_column_if_needed(cr, table, old, new):
    if _column_exists(cr, table, old) and not _column_exists(cr, table, new):
        cr.execute('ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % (table, old, new))



def _replace_view_arch_field_names(cr):
    for old, new in FIELD_RENAMES.values():
        pass



def pre_init_hook(cr):
    # 1) Rename stored columns before model initialization.
    for table, mapping in COLUMN_RENAMES.items():
        for old, new in mapping.items():
            _rename_column_if_needed(cr, table, old, new)

    # 2) Rewrite any view XML that still references old field names.
    for (model, old_name), new_name in FIELD_RENAMES.items():
        cr.execute(
            """
            UPDATE ir_ui_view
               SET arch_db = replace(arch_db, %s, %s)
             WHERE arch_db LIKE %s
            """,
            (old_name, new_name, '%%%s%%' % old_name),
        )

    # 3) Disable the narrow Studio views that are replaced by module XML.
    for model, name in STUDIO_VIEWS_TO_DISABLE:
        cr.execute(
            """
            UPDATE ir_ui_view
               SET active = FALSE
             WHERE model = %s
               AND name = %s
            """,
            (model, name),
        )

    # 4) Remove old manual field definitions so the module can own the new names.
    old_field_ids = []
    for (model, old_name), _new_name in FIELD_RENAMES.items():
        cr.execute(
            """
            SELECT id
              FROM ir_model_fields
             WHERE model = %s
               AND name = %s
            """,
            (model, old_name),
        )
        old_field_ids.extend(row[0] for row in cr.fetchall())

    if old_field_ids:
        cr.execute(
            "DELETE FROM ir_model_data WHERE model = 'ir.model.fields' AND res_id = ANY(%s)",
            (old_field_ids,),
        )
        cr.execute(
            "DELETE FROM ir_model_fields_selection WHERE field_id = ANY(%s)",
            (old_field_ids,),
        )
        cr.execute(
            "DELETE FROM ir_model_fields WHERE id = ANY(%s)",
            (old_field_ids,),
        )



def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    company_currency = env.company.currency_id
    categories = env['product.category'].with_context(active_test=False).search([])
    for categ in categories.filtered(lambda c: not c.sid_currency_id):
        categ.sid_currency_id = company_currency

    # Recompute and normalize stored values owned by the module.
    products = env['product.template'].with_context(active_test=False).search([])
    products._compute_sid_cost_category()

    lines = env['sale.order.line'].with_context(active_test=False).search([('product_id', '!=', False)])
    for line in lines:
        line.sid_cost_category = line.product_id.sid_cost_category
