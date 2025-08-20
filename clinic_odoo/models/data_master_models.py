from odoo import models, fields, api

class mst_service_types(models.Model):
    _name = 'mst.service.types'
    _description = 'Menu Master Jenis Pelayanan'

    nomer = fields.Char(string='Kode Pelayanan', required=True)
    name = fields.Char(string='Nama Jenis Pelayanan', required=True)
    description = fields.Text(string='Keterangan')
    poli_ids = fields.One2many('mst.poli', 'service_type_id', string='Poli')

class mst_poli(models.Model):
    _name = 'mst.poli'
    _description = 'Master Poli'

    kode = fields.Char(string='Kode Poli', required=True)
    name = fields.Char(string='Nama Poli', required=True)
    description = fields.Text(string='Keterangan')
    service_type_id = fields.Many2one('mst.service.types', string='Jenis Pelayanan', required=True, ondelete='cascade')
    divisi_ids = fields.One2many('mst.divisi', 'poli_id', string='Divisi')

class mst_divisi(models.Model):
    _name = 'mst.divisi'
    _description = 'Master Divisi'
    _rec_name = 'name'

    kode = fields.Char(string='Kode Divisi', required=True)
    name = fields.Char(string='Nama Divisi', required=True)
    description = fields.Text(string='Keterangan')

    # relasi ke Poli (wajib) → otomatis memetakan Divisi di bawah Poli
    poli_id = fields.Many2one('mst.poli', string='Poli', required=True, ondelete='cascade')

    # relasi turunan (opsional tapi berguna untuk filter/search)
    service_type_id = fields.Many2one(
        related='poli_id.service_type_id',
        string='Jenis Pelayanan',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        ('mst_divisi_kode_unique', 'unique(kode)', 'Kode Divisi harus unik!'),
    ]