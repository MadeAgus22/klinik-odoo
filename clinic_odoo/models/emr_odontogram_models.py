# clinic_odoo/models/emr_odontogram_models.py
from odoo import models, fields

class EmrOdontogram(models.Model):
    _name = 'emr.odontogram'
    _description = 'Data Odontogram'

    name = fields.Char(string='Nama', default='Odontogram')
    # Data JSON disimpan sebagai teks panjang
    odontogram_data = fields.Text(string='Data JSON')