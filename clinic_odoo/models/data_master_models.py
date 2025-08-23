from odoo import models, fields, api
from odoo.exceptions import ValidationError

class mst_service_types(models.Model):
    _name = 'mst.service.types'
    _description = 'Menu Master Jenis Pelayanan'

    nomer = fields.Char(string='Kode Pelayanan', required=True)
    name = fields.Char(string='Nama Jenis Pelayanan', required=True)
    description = fields.Text(string='Keterangan')
    poli_ids = fields.One2many('mst.poli', 'service_type_id', string='Poli')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.nomer or ''} - {rec.name or ''}".strip()))
        return res

class mst_poli(models.Model):
    _name = 'mst.poli'
    _description = 'Master Poli'

    kode = fields.Char(string='Kode Poli', required=True)
    name = fields.Char(string='Nama Poli', required=True)
    description = fields.Text(string='Keterangan')
    service_type_id = fields.Many2one('mst.service.types', string='Jenis Pelayanan', required=True, ondelete='cascade')
    divisi_ids = fields.One2many('mst.divisi', 'poli_id', string='Divisi')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.kode or ''} - {rec.name or ''}".strip()))
        return res
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

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, f"{rec.kode or ''} - {rec.name or ''}".strip()))
        return res

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

    tarif_ids = fields.One2many('mst.tarif.tindakan', 'produk_id', string='Tarif')
    
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
    tarif_ids = fields.One2many('mst.tarif.obat', 'produk_id', string='Tarif Obat')

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
    tarif_ids = fields.One2many('mst.tarif.alatkesehatan', 'produk_id', string='Tarif Alat Kesehatan')

    _sql_constraints = [
        ('kode_alat_unique', 'unique(kode)', 'Kode Alat harus unik!'),
    ]

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

class mst_tarif_tindakan(models.Model):
    _name = 'mst.tarif.tindakan'
    _description = 'Master Tarif Tindakan'
    _rec_name = 'kode'

    kode = fields.Char(string='Kode Tarif', required=True)
    produk_id = fields.Many2one('mst.produk.tindakan', string='Nama Produk', required=True, ondelete='restrict')
    kelas_id  = fields.Many2one('mst.kelas.tarif', string='Kelas', required=True, ondelete='restrict')

    currency_id = fields.Many2one('res.currency', string='Mata Uang',
                                  default=lambda self: self.env.company.currency_id.id, required=True)

    jasa_klinik   = fields.Monetary(string='Jasa Klinik', default=0.0, currency_field='currency_id')
    jasa_admin    = fields.Monetary(string='Jasa Admin', default=0.0, currency_field='currency_id')
    jasa_operator = fields.Monetary(string='Jasa Operator', default=0.0, currency_field='currency_id')
    jasa_lainnya  = fields.Monetary(string='Jasa Lainnya', default=0.0, currency_field='currency_id')

    total_tarif = fields.Monetary(string='Total Tarif', compute='_compute_total_tarif',
                                  store=True, currency_field='currency_id')

    date_start = fields.Date(string='Tanggal Awal')
    date_end   = fields.Date(string='Tanggal Akhir')
    active     = fields.Boolean(string='Aktif', default=True)
    description = fields.Text(string='Catatan')

    _sql_constraints = [
        ('kode_tarif_tindakan_unique', 'unique(kode)', 'Kode Tarif harus unik!'),
    ]

    @api.depends('jasa_klinik', 'jasa_admin', 'jasa_operator', 'jasa_lainnya')
    def _compute_total_tarif(self):
        for rec in self:
            rec.total_tarif = (rec.jasa_klinik or 0.0) + (rec.jasa_admin or 0.0) + (rec.jasa_operator or 0.0) + (rec.jasa_lainnya or 0.0)

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

class mst_tarif_obat(models.Model):
    _name = 'mst.tarif.obat'
    _description = 'Master Tarif Obat'
    _rec_name = 'kode'

    kode = fields.Char(string='Kode Tarif', required=True)
    produk_id = fields.Many2one('mst.produk.obat', string='Nama Produk', required=True, ondelete='restrict')
    kelas_id  = fields.Many2one('mst.kelas.tarif', string='Kelas', required=True, ondelete='restrict')

    currency_id = fields.Many2one(
        'res.currency', string='Mata Uang',
        default=lambda self: self.env.company.currency_id.id, required=True)

    # Komponen tarif (samakan dengan tindakan sesuai permintaan)
    jasa_klinik   = fields.Monetary(string='Jasa Klinik',  default=0.0, currency_field='currency_id')
    jasa_admin    = fields.Monetary(string='Jasa Admin',   default=0.0, currency_field='currency_id')
    jasa_operator = fields.Monetary(string='Jasa Operator',default=0.0, currency_field='currency_id')
    jasa_lainnya  = fields.Monetary(string='Jasa Lainnya', default=0.0, currency_field='currency_id')

    total_tarif = fields.Monetary(
        string='Total Tarif', compute='_compute_total_tarif', store=True,
        currency_field='currency_id')

    date_start = fields.Date(string='Tanggal Awal')
    date_end   = fields.Date(string='Tanggal Akhir')
    active     = fields.Boolean(string='Aktif', default=True)
    description = fields.Text(string='Catatan')

    _sql_constraints = [
        ('kode_tarif_obat_unique', 'unique(kode)', 'Kode Tarif harus unik!'),
    ]

    @api.depends('jasa_klinik', 'jasa_admin', 'jasa_operator', 'jasa_lainnya')
    def _compute_total_tarif(self):
        for rec in self:
            rec.total_tarif = (rec.jasa_klinik or 0.0) + (rec.jasa_admin or 0.0) + (rec.jasa_operator or 0.0) + (rec.jasa_lainnya or 0.0)

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

class mst_tarif_alatkesehatan(models.Model):
    _name = 'mst.tarif.alatkesehatan'
    _description = 'Master Tarif Alat Kesehatan'
    _rec_name = 'kode'

    kode = fields.Char(string='Kode Tarif', required=True)
    produk_id = fields.Many2one('mst.produk.alatkesehatan', string='Nama Produk', required=True, ondelete='restrict')
    kelas_id  = fields.Many2one('mst.kelas.tarif', string='Kelas', required=True, ondelete='restrict')

    currency_id = fields.Many2one(
        'res.currency', string='Mata Uang',
        default=lambda self: self.env.company.currency_id.id, required=True)

    jasa_klinik   = fields.Monetary(string='Jasa Klinik',   default=0.0, currency_field='currency_id')
    jasa_admin    = fields.Monetary(string='Jasa Admin',    default=0.0, currency_field='currency_id')
    jasa_operator = fields.Monetary(string='Jasa Operator', default=0.0, currency_field='currency_id')
    jasa_lainnya  = fields.Monetary(string='Jasa Lainnya',  default=0.0, currency_field='currency_id')

    total_tarif = fields.Monetary(
        string='Total Tarif', compute='_compute_total_tarif', store=True,
        currency_field='currency_id')

    date_start = fields.Date(string='Tanggal Awal')
    date_end   = fields.Date(string='Tanggal Akhir')
    active     = fields.Boolean(string='Aktif', default=True)
    description = fields.Text(string='Catatan')

    _sql_constraints = [
        ('kode_tarif_alatkesehatan_unique', 'unique(kode)', 'Kode Tarif harus unik!'),
    ]

    @api.depends('jasa_klinik', 'jasa_admin', 'jasa_operator', 'jasa_lainnya')
    def _compute_total_tarif(self):
        for rec in self:
            rec.total_tarif = (rec.jasa_klinik or 0.0) + (rec.jasa_admin or 0.0) + (rec.jasa_operator or 0.0) + (rec.jasa_lainnya or 0.0)

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    unit_pelayanan_ids = fields.One2many('mst.unit.pelayanan.dokter', 'employee_id', string='Unit Pelayanan Dokter')

class mst_unit_pelayanan_dokter(models.Model):
    _name = 'mst.unit.pelayanan.dokter'
    _description = 'Mapping Unit Pelayanan Dokter'
    _rec_name = 'code'
    _order = 'employee_id, service_type_id, poli_id, divisi_id, id'

    code = fields.Char(string='Kode', required=True, copy=False, readonly=True, default='New')
    employee_id = fields.Many2one(
        'hr.employee', string='Dokter', required=True, ondelete='cascade',
        help='Dokter yang dipetakan ke unit pelayanan.'
    )

    # Pilih salah satu sumber: Jenis Pelayanan / Poli / Divisi
    pelayanan_ref = fields.Reference(
        selection=[
            ('mst.service.types', 'Jenis Pelayanan'),
            ('mst.poli',          'Poli'),
            ('mst.divisi',        'Divisi'),
        ],
        string='Pelayanan', required=True,
        help='Pilih salah satu level unit pelayanan.'
    )

    # --- Helper fields (diset otomatis dari pelayanan_ref) ---
    service_type_id = fields.Many2one('mst.service.types', string='Jenis Pelayanan', index=True,
                                      compute='_compute_keys', store=True, readonly=True)
    poli_id         = fields.Many2one('mst.poli',          string='Poli',            index=True,
                                      compute='_compute_keys', store=True, readonly=True)
    divisi_id       = fields.Many2one('mst.divisi',        string='Divisi',          index=True,
                                      compute='_compute_keys', store=True, readonly=True)

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Kode mapping harus unik.'),
    ]

    @api.depends('pelayanan_ref')
    def _compute_keys(self):
        """Turunkan jenjang hirarki dari pilihan Reference agar gampang di-domain di tempat lain."""
        for rec in self:
            rec.service_type_id = False
            rec.poli_id = False
            rec.divisi_id = False
            pr = rec.pelayanan_ref
            if not pr:
                continue
            if pr._name == 'mst.service.types':
                rec.service_type_id = pr
            elif pr._name == 'mst.poli':
                rec.poli_id = pr
                rec.service_type_id = pr.service_type_id
            elif pr._name == 'mst.divisi':
                rec.divisi_id = pr
                rec.poli_id = pr.poli_id
                rec.service_type_id = pr.poli_id.service_type_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code') or vals.get('code') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('mst.unit.pelayanan.dokter') or '/'
        return super().create(vals_list)

    # Pastikan satu baris mapping tidak diduplikasi (employee + titik tujuan sama)
    @api.constrains('employee_id', 'service_type_id', 'poli_id', 'divisi_id')
    def _check_duplicate(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('employee_id', '=', rec.employee_id.id),
                ('service_type_id', '=', rec.service_type_id.id or False),
                ('poli_id', '=', rec.poli_id.id or False),
                ('divisi_id', '=', rec.divisi_id.id or False),
            ]
            if self.search_count(domain):
                raise ValidationError(_('Mapping dokter ini sudah ada untuk unit yang sama.'))

    # (opsional) tampilkan nama yang informatif
    def name_get(self):
        res = []
        for rec in self:
            part = rec.divisi_id.name or rec.poli_id.name or rec.service_type_id.name or '-'
            name = f"{rec.employee_id.name} - {part}"
            res.append((rec.id, name))
        return res