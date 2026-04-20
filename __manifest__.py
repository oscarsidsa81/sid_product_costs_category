# -*- coding: utf-8 -*-
{
 'name' : 'sid_product_cost_category',
 'version' : '15.0.1.0.0',
 'category' : 'Inventory',
 'summary' : 'Take ownership of Studio cost fields and views in code.',
 'author' : 'oscarsidsa81',
 'license' : 'LGPL-3',
 'depends' : ['product', 'sale_management'],
 'data' : [
     'views/product_category_views.xml',
     'views/product_template_views.xml',
     'views/sale_order_views.xml',
 ],
 'pre_init_hook' : 'pre_init_hook',
 'post_init_hook' : 'post_init_hook',
 'installable' : True,
 'application' : False
}
