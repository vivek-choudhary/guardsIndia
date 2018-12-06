# -*- coding: utf-8 -*-
{
    'name': "Guards BOM Form Widget",

    'summary': """Module for BOM widget""",

    'description': """
        No description
    """,

    'author': "Sudhanshu Gupta",
    'website': "http://www.mesudhanshu.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'guards_sale', 'guards_product', 'guards_product_bom'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/bom_widget.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'qweb': ['static/src/xml/*.xml'],
}