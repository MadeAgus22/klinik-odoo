# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class emr_record(models.Model):
    _name = 'emr.record'
    _description = 'Electronic Medical Record'

    name = fields.Char(string='Nomor EMR', default=lambda s: _('New'), copy=False)

    patient_id   = fields.Many2one('pfn.data.pasien', string='Pasien', required=True, ondelete='restrict')
    kunjungan_id = fields.Many2one('pfn.kunjungan.pasien', string='Kunjungan', required=True, ondelete='cascade')
    doctor_id    = fields.Many2one('hr.employee', string='Dokter', ondelete='restrict')

    # Biodata (related)
    no_rm        = fields.Char(related='patient_id.no_rm', string='No. RM', store=True, readonly=True)
    gender       = fields.Selection(related='patient_id.gender', string='Jenis Kelamin', store=True, readonly=True)
    umur_display = fields.Char(related='patient_id.umur_display', string='Umur', store=True, readonly=True)
    phone        = fields.Char(related='patient_id.phone', string='HP', store=True, readonly=True)
    email        = fields.Char(related='patient_id.email', string='E-mail', store=True, readonly=True)
    alamat       = fields.Char(related='patient_id.alamat', string='Alamat', store=True, readonly=True)

    # Registrasi (related)
    service_type_id = fields.Many2one(related='kunjungan_id.service_type_id', string='Jenis Pelayanan', store=True, readonly=True)
    poli_id         = fields.Many2one(related='kunjungan_id.poli_id', string='Poli', store=True, readonly=True)
    divisi_id       = fields.Many2one(related='kunjungan_id.divisi_id', string='Divisi', store=True, readonly=True)
    visit_datetime  = fields.Datetime(related='kunjungan_id.visit_datetime', string='Tanggal & Jam', store=True, readonly=True)
    queue_no        = fields.Integer(related='kunjungan_id.queue_no', string='No. Antrian', store=True, readonly=True)
    status_pelayanan = fields.Selection(
        related='kunjungan_id.status_pelayanan',
        string='Status Pelayanan',
        store=True,
        readonly=True,
    )

    # === SOAP ===
    # Subyektif
    subj_keluhan        = fields.Text(string='Keluhan')
    subj_riwayat_peny   = fields.Text(string='Riwayat Penyakit')
    subj_riwayat_alergi = fields.Text(string='Riwayat Alergi')

    # Obyektif
    obj_td_sistol  = fields.Integer(string='Tekanan Darah (Sistol)')
    obj_td_diastol = fields.Integer(string='Tekanan Darah (Diastol)')
    obj_nadi       = fields.Integer(string='Denyut Nadi / menit')
    obj_suhu       = fields.Float(string='Suhu Tubuh (°C)')
    obj_pemeriksaan_fisik = fields.Text(string='Pemeriksaan Fisik')

    # Assessment
    diagnosis_line_ids = fields.One2many('emr.diagnosis.line', 'emr_id', string='Diagnosis')
    prognosis = fields.Selection([
        ('sanam', 'Sanam (Sembuh)'),
        ('bonam', 'Bonam (Baik)'),
        ('malam', 'Malam (Buruk)'),
        ('dubia_sanam', 'Dubia ad sanam (Ragu ke sembuh)'),
        ('dubia_malam', 'Dubia ad malam (Ragu ke buruk)'),
    ], string='Prognosis')

    # Plan
    procedure_line_ids     = fields.One2many('emr.procedure.line', 'emr_id', string='Prosedur')
    prescription_line_ids  = fields.One2many('emr.prescription.line', 'emr_id', string='Resep')
    edukasi           = fields.Text(string='Edukasi')
    rencana_tindakan  = fields.Text(string='Rencana Tindakan')
    rencana_tanggal   = fields.Date(string='Tanggal Rencana')
    rencana_catatan   = fields.Text(string='Catatan Rencana')

    _sql_constraints = [
        ('emr_per_visit_unique', 'unique(kunjungan_id)', 'EMR untuk kunjungan ini sudah ada.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('emr.record.seq') or _('New')
        return super().create(vals_list)


class emr_diagnosis_line(models.Model):
    _name = 'emr.diagnosis.line'
    _description = 'EMR Diagnosis Line'
    _order = 'id asc'

    emr_id = fields.Many2one('emr.record', string='EMR', ondelete='cascade', required=True)
    diagnosa_name = fields.Char(string='Nama Diagnosa')
    icd10_name    = fields.Char(string='Nama ICD-10')
    icd10_code    = fields.Char(string='Kode ICD-10')


class emr_procedure_line(models.Model):
    _name = 'emr.procedure.line'
    _description = 'EMR Procedure Line'
    _order = 'id asc'

    emr_id = fields.Many2one('emr.record', string='EMR', ondelete='cascade', required=True)
    tindakan_id   = fields.Many2one('mst.produk.tindakan', string='Tindakan')  # sesuaikan bila nama model master tindakan berbeda
    tindakan_code = fields.Char(related='tindakan_id.kode', string='Kode', store=True, readonly=True)  # <- gunakan 'kode'
    tindakan_name = fields.Char(related='tindakan_id.name', string='Nama', store=True, readonly=True)


class emr_prescription_line(models.Model):
    _name = 'emr.prescription.line'
    _description = 'EMR Prescription Line'
    _order = 'id asc'

    emr_id = fields.Many2one('emr.record', string='EMR', ondelete='cascade', required=True)
    obat_id   = fields.Many2one('mst.produk.obat', string='Obat')  # sesuaikan bila nama model master obat berbeda
    obat_name = fields.Char(related='obat_id.name', string='Nama Obat', store=True, readonly=True)
    note      = fields.Char(string='Catatan')
