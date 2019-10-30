# -*- coding: utf-8 -*-
# Copyright 2019 Guadaltech Soluciones Tecnológicas S.L (<http://guadaltech.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': "Recever Integration",
    'description': """Creation of Recevers and iRecevers that are send to the customer account. 
    IMPORTANT: We use the customer data obtained from the Recever integration in order to make the invoices.""",

    'author': "Guadaltech Soluciones Tecnológicas S.L",
    'website': "http://www.guadaltech.es - https://www.recever.app/",

    'category': "Point of Sale",
    'version': '12.0.1.0.0',

    'depends': ['point_of_sale','base', 'pos_sale'],

    'data': [
        'views/assets_extension.xml',
        'views/pos_recever.xml',
        'security/ir.model.access.csv',
        'wizard/custom_wizard.xml'
    ],
    'qweb': ['static/src/xml/recever.xml'],
    'installable': True,
    'images': ['static/description/Banner.jpg'],
    'license': 'LGPL-3',
    'support': 'hola@guadaltech.es',
    'installable': True,
    'auto_install': False,
    'application': True,
}
