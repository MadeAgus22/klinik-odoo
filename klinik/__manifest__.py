# -*- coding: utf-8 -*-
{
    'name': "Klinik Sederhana",

    'summary': """
        Modul untuk manajemen klinik sederhana""",

    'description': """
        Modul ini mencakup pendaftaran pasien untuk rawat jalan, rawat darurat, dan rawat inap.
    """,

    'author': "Anda (MadeAgus)",
    'website': "https://absensi-lovat-seven.vercel.app/",

    'category': 'Services/Klinik',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',

    "depends": ["product", "stock", "sale"],

    # selalu dimuat
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/product_views.xml",
    ],

    # hanya dimuat dalam mode demo
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
}