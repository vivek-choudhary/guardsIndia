# -*- coding: utf-8 -*-
{
    'name': "Project Initial",

    'summary': """
        Initail module for the project""",

    'description': """
        Module is used for:
        1. Updating home route.
        2. Updating login page.
        3. Creation of groups.
        4. Creation of tools
    """,

    'author': "Sudhanshu Gupta",
    'website': "http://www.mesudhanshu.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/groups.xml',
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/inherit_webclient_template.xml',
        'data/smtp.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb':[
        'static/src/xml/inherit_systray.xml',
        'static/src/xml/inherit_base.xml',
    ],
}
