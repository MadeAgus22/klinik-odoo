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
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/sequence_unit_pelayanan.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/mst_service_types_views.xml',
        'views/mst_poli_views.xml',
        'views/mst_divisi_views.xml',
        'views/mst_kelas_tarif_views.xml',
        'views/mst_produk_views.xml',
        'views/mst_tarif_tindakan_embed_views.xml',
        'views/mst_tarif_obat_embed_views.xml',
        'views/mst_tarif_alatkesehatan_embed_views.xml',
        'views/mst_unit_pelayanan_dokter_embed_views.xml',
        'views/pfn_data_pasien_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
}

