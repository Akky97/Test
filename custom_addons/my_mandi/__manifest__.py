# -*- coding: utf-8 -*-
{
    'name': "My Mandi Odoo REST API",

    'summary': """
        My Mandi Odoo REST API""",

    'description': """
        My Mandi Odoo REST API
    """,

    'author': "Yezileli Ilomo",
    'website': "https://github.com/yezyilomo/odoo-rest-api",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'developers',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'website_sale'],

    # always loaded
    'data': [
        'data/ir_config_param.xml',
        'security/security.xml',
        'views/res_users.xml',
        'views/procurement_table.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml'
    ],

    "application": True,
    "installable": True,
    "auto_install": False,

    'external_dependencies': {
        'python': ['pypeg2']
    }
}
