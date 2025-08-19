from odoo import models, fields, api

class mst_service_types(models.Model):
    _name = 'mst.service.types'
    _description = 'Menu Master Jenis Pelayanan'

    nomer = fields.Integer(string='Nomer', required=True)
    name = fields.Char(string='Nama Jenis Pelayanan', required=True)
    description = fields.Text(string='Keterangan')

class mst_sub_service(models.Model):
    _name = 'mst.sub.service'
    _description = 'Menu untuk membuat Sub dari Jenis Pelayanan'

    nomer = fields.Integer(string='nomer', required=True)
    name = fields.Char(string='Nama Sub-Pelayanan', required=True)
    description = fields.Text(string='Keteangan')

    