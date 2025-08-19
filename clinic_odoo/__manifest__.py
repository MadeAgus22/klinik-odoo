# -*- coding: utf-8 -*-
{
    'name': "clinic_odoo",

    'summary': "Sistem klinik odoo",

    'description': """
Sistem klinik odoo dalam pengembangan akan terus berkembang mengikuti perkembangan jaman
    """,

    'author': "Toni Saputra",
    'website': "https://absensi-lovat-seven.vercel.app/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Healthcare',
    'version': '0.01',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
}

