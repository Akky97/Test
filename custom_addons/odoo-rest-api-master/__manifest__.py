# -*- coding: utf-8 -*-
{
    'name': "Odoo REST API",

    'summary': """
        Odoo REST API""",

    'description': """
        Odoo REST API
    """,

    'author': "Yezileli Ilomo",
    'website': "https://github.com/yezyilomo/odoo-rest-api",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'developers',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'website_sale', 'payment', 'odoo_marketplace'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/ir_model.xml',
        'views/res_users.xml',
        'data/ir_config_param.xml',
        'views/pando_banner.xml',
        'views/pando_image_view.xml',
        'views/product_template.xml',
        'views/category_view.xml',
        'security/ir.model.access.csv',
        'views/email_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    "application": True,
    "installable": True,
    "auto_install": False,

    'external_dependencies': {
        'python': ['pypeg2']
    }
}
