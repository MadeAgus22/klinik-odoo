# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class EmrOdontogram(models.Model):
    _name = 'emr.odontogram'
    _description = 'EMR Odontogram'

    emr_id = fields.Many2one(
        'emr.record', string='EMR', required=True, ondelete='cascade',
        help='Relasi ke EMR Record (kunjungan pasien).')
    odontogram_data = fields.Text(
        string='Data Odontogram',
        help='JSON atau string hasil input odontogram (colours, tag, missing, dsb.).')

    _sql_constraints = [
        ('emr_unique', 'unique(emr_id)',
         'Satu EMR hanya boleh memiliki satu odontogram.')
    ]
