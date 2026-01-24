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

    def action_open_schedule(self):
        self.ensure_one()
        return {
            'name': f"Jadwal: {self.employee_id.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'set.doctors.schedule',
            'view_mode': 'calendar,list,form',
            # DOMAIN: Filter agar kalender hanya memunculkan data dokter ini
            'domain': [('doctor_id', '=', self.employee_id.id)],
            # CONTEXT: Default value saat user membuat jadwal baru (klik tanggal)
            'context': {
                'default_doctor_id': self.employee_id.id,
                # Kita HAPUS 'search_default_...' yang bikin error. 
                # Domain di atas sudah cukup untuk memfilter data.
            },
        }

# ==============================================================================
# MAPPING PRODUK & OBAT (FINAL)
# ==============================================================================

class ClinicMappingObat(models.Model):
    _name = 'clinic.mapping.obat'
    _description = 'Mapping Kategori Obat EMR'
    _rec_name = 'service_type_id'  # Ubah rec_name agar lebih informatif

    service_type_id = fields.Many2one(
        'mst.service.types', 
        string='Jenis Pelayanan', 
        required=True,
        ondelete='cascade'
    )
    product_category_id = fields.Many2one(
        'product.category', 
        string='Kategori Produk (Inventory)', 
        required=True,
        ondelete='cascade',
        help="Semua produk dalam kategori ini akan muncul sebagai 'Obat' di EMR pada pelayanan tersebut"
    )
    description = fields.Text(string='Keterangan')
    
    # Constraint diupdate: Unik berdasarkan PASANGAN (Layanan + Kategori)
    _sql_constraints = [
        ('mapping_obat_unique', 'unique(service_type_id, product_category_id)', 'Kategori produk ini sudah terdaftar untuk pelayanan tersebut!'),
    ]

    def name_get(self):
        res = []
        for rec in self:
            srv_name = rec.service_type_id.name or '?'
            cat_name = rec.product_category_id.name or '?'
            name = f"{srv_name} -> {cat_name}"
            res.append((rec.id, name))
        return res

class ClinicMappingProduk(models.Model):
    _name = 'clinic.mapping.produk'
    _description = 'Mapping Kategori Produk per Layanan'
    _rec_name = 'service_type_id'

    service_type_id = fields.Many2one(
        'mst.service.types', 
        string='Jenis Pelayanan', 
        required=True,
        ondelete='cascade'
    )
    product_category_id = fields.Many2one(
        'product.category', 
        string='Kategori Produk (Inventory)', 
        required=True,
        ondelete='cascade',
        help="Produk dalam kategori ini akan muncul saat layanan ini dipilih di EMR"
    )
    description = fields.Text(string='Keterangan')

    # --- UPGRADE: Mencegah duplikasi pasangan Layanan + Kategori ---
    _sql_constraints = [
        ('mapping_produk_unique', 'unique(service_type_id, product_category_id)', 'Kategori produk ini sudah dipetakan untuk layanan tersebut!'),
    ]

    def name_get(self):
        res = []
        for rec in self:
            # Gunakan .name atau string kosong jika belum diset
            srv_name = rec.service_type_id.name or '?'
            cat_name = rec.product_category_id.name or '?'
            name = f"{srv_name} -> {cat_name}"
            res.append((rec.id, name))
        return res
    
#==============================================================================
class MstSesiPelayanan(models.Model):
    _name = 'mst.sesi.pelayanan'
    _description = 'Master Sesi Pelayanan'
    _rec_name = 'name'

    # Buat daftar pilihan Jam (00-23) dan Menit (00-59)
    # zfill(2) membuat angka 1 menjadi '01'
    SELECTION_JAM = [(str(i).zfill(2), str(i).zfill(2)) for i in range(24)]
    SELECTION_MENIT = [(str(i).zfill(2), str(i).zfill(2)) for i in range(60)]

    name = fields.Char(string='Nama Sesi', required=True)
    
    # Jam Awal (Dipisah)
    awal_jam = fields.Selection(SELECTION_JAM, string='Jam Awal', required=True, default='08')
    awal_menit = fields.Selection(SELECTION_MENIT, string='Menit Awal', required=True, default='00')

    # Jam Akhir (Dipisah)
    akhir_jam = fields.Selection(SELECTION_JAM, string='Jam Akhir', required=True, default='16')
    akhir_menit = fields.Selection(SELECTION_MENIT, string='Menit Akhir', required=True, default='00')

    catatan = fields.Text(string='Catatan')

    # Field Compute: Menggabungkan Jam & Menit untuk tampilan di List View
    jam_awal_display = fields.Char(string='Waktu Mulai', compute='_compute_waktu_display')
    jam_akhir_display = fields.Char(string='Waktu Selesai', compute='_compute_waktu_display')

    waktu_kerja = fields.Char(string='Durasi Kerja', compute='_compute_waktu_display')

    @api.depends('awal_jam', 'awal_menit', 'akhir_jam', 'akhir_menit')
    def _compute_waktu_display(self):
        for rec in self:
            # 1. Set Display Waktu Mulai & Selesai
            rec.jam_awal_display = f"{rec.awal_jam}:{rec.awal_menit}" if rec.awal_jam and rec.awal_menit else ""
            rec.jam_akhir_display = f"{rec.akhir_jam}:{rec.akhir_menit}" if rec.akhir_jam and rec.akhir_menit else ""

            # 2. Hitung Durasi Kerja
            if rec.awal_jam and rec.akhir_jam:
                # Konversi ke total menit untuk perhitungan
                start_total = (int(rec.awal_jam) * 60) + int(rec.awal_menit)
                end_total = (int(rec.akhir_jam) * 60) + int(rec.akhir_menit)

                # Logika jika waktu selesai melewati tengah malam (misal 22:00 - 02:00)
                if end_total <= start_total:
                    diff_total = (1440 - start_total) + end_total # 1440 adalah total menit dlm 1 hari
                else:
                    diff_total = end_total - start_total

                hours = diff_total // 60
                minutes = diff_total % 60
                rec.waktu_kerja = f"{hours} jam {minutes} menit"
            else:
                rec.waktu_kerja = "0 jam 0 menit"