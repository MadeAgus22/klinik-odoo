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

class mst_kelas_tarif(models.Model):
    _name = 'mst.kelas.tarif'
    _description = 'Master Grup Kelas Tarif'
    _rec_name = 'name'

    kode = fields.Char(string='Kode Kelas', required=True)
    name = fields.Char(string='Nama Kelas', required=True)
    description = fields.Text(string='Catatan')
    active = fields.Boolean(string='Status', default=True)

    _sql_constraints = [
        ('kelas_kode_unique', 'unique(kode)', 'Kode Kelas harus unik!'),
    ]

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

# --- MASTER PRODUK: TINDAKAN ---
class mst_produk_tindakan(models.Model):
    _name = 'mst.produk.tindakan'
    _description = 'Master Produk - Tindakan'
    _rec_name = 'name'

    kode = fields.Char(string='Kode', required=True)
    name = fields.Char(string='Nama Tindakan', required=True)
    description = fields.Text(string='Catatan')
    active = fields.Boolean(string='Status', default=True)

    _sql_constraints = [
        ('kode_tindakan_unique', 'unique(kode)', 'Kode Tindakan harus unik!'),
    ]

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active


# --- MASTER PRODUK: OBAT ---
class mst_produk_obat(models.Model):
    _name = 'mst.produk.obat'
    _description = 'Master Produk - Obat'
    _rec_name = 'name'

    kode = fields.Char(string='Kode', required=True)
    name = fields.Char(string='Nama Obat', required=True)
    description = fields.Text(string='Catatan')
    active = fields.Boolean(string='Status', default=True)

    _sql_constraints = [
        ('kode_obat_unique', 'unique(kode)', 'Kode Obat harus unik!'),
    ]

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active


# --- MASTER PRODUK: ALAT KESEHATAN ---
class mst_produk_alatkesehatan(models.Model):
    _name = 'mst.produk.alatkesehatan'
    _description = 'Master Produk - Alat Kesehatan'
    _rec_name = 'name'

    kode = fields.Char(string='Kode', required=True)
    name = fields.Char(string='Nama Alat', required=True)
    description = fields.Text(string='Catatan')
    active = fields.Boolean(string='Status', default=True)

    _sql_constraints = [
        ('kode_alat_unique', 'unique(kode)', 'Kode Alat harus unik!'),
    ]

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

            