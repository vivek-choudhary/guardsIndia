# -*- coding: utf-8 -*-
{
    'name': "Guards Payment Module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sudhanshu Gupta",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','mail'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/cron.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/inherit_res_partner.xml',
        'views/inherit_res_company.xml',
        'data/mail_group.xml',
        'data/mail_template.xml',
        'data/company_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/widget.xml'],
}