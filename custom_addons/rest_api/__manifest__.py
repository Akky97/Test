# -*- coding: utf-8 -*-
{
    'name': 'Professional REST API',
    'version': '11.0.1.6.1',
    'category': 'Extra Tools',
    'author': 'Andrey Sinyanskiy SP',
    'support': 'avs3.ua@gmail.com',
    'license': 'OPL-1',
    'price': 129.00,
    'currency': 'EUR',
    'summary': 'Professional RESTful API access to Odoo models with predefined and tree-like schema of response Odoo fields',
    #'description': < auto-loaded from README file
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'data/ir_configparameter_data.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
