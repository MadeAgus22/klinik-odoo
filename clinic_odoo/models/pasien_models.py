# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import random
import re


# =========================
#   DATA PASIEN
# =========================
class pfn_data_pasien(models.Model):
    _name = 'pfn.data.pasien'
    _description = 'Pendaftaran - Data Pasien'
    _rec_name = 'name'

    # Identitas
    no_rm = fields.Char(
        string='Nomer Rekam Medis',
        required=True, copy=False, readonly=True, index=True,
        default='New',
        help="Otomatis: 8 digit YYMM + 4 digit acak, misal 25080188."
    )
    name = fields.Char(string='Nama Lengkap', required=True, index=True)
    no_identitas = fields.Char(string='No. KTP', required=True, index=True)
    tempat_lahir = fields.Char(string='Tempat Lahir', required=True)
    tanggal_lahir = fields.Date(string='Tanggal Lahir', required=True)

    umur_display = fields.Char(
        string='Umur', compute='_compute_umur', store=True, readonly=True)

    gender = fields.Selection(
        [('male', 'Laki-laki'), ('female', 'Perempuan')],
        string='Jenis Kelamin', required=True
    )
    phone = fields.Char(string='Nomer HP', required=True)
    email = fields.Char(string='E-mail', required=True)
    alamat = fields.Char(string='Alamat', required=True)

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('no_rm_unique', 'unique(no_rm)', 'Nomer Rekam Medis harus unik!'),
        ('no_identitas_unique', 'unique(no_identitas)', 'No. KTP sudah digunakan!'),
    ]

    # Relasi → kunjungan pasien
    kunjungan_ids = fields.One2many(
        'pfn.kunjungan.pasien', 'patient_id',
        string='Kunjungan Pasien'
    )

    # Status Pelayanan (untuk list pasien/EMR)
    emr_status_pelayanan = fields.Char(
        string='Status Pelayanan',
        compute='_compute_emr_status_pelayanan',
        readonly=True,
    )

    # ---------- computes / constrains ----------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('no_rm') or vals.get('no_rm') == 'New':
                today = fields.Date.context_today(self)
                yy = f"{today.year % 100:02d}"
                mm = f"{today.month:02d}"
                while True:
                    rand4 = f"{random.randint(0, 9999):04d}"
                    candidate = f"{yy}{mm}{rand4}"
                    if not self.search_count([('no_rm', '=', candidate)]):
                        vals['no_rm'] = candidate
                        break
        return super().create(vals_list)

    @api.depends('tanggal_lahir')
    def _compute_umur(self):
        today = date.today()
        for rec in self:
            if rec.tanggal_lahir:
                rd = relativedelta(today, rec.tanggal_lahir)
                rec.umur_display = _("%s tahun %s bulan") % (rd.years, rd.months)
            else:
                rec.umur_display = False

    @api.constrains('email')
    def _check_email(self):
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        for rec in self:
            if rec.email and not re.match(pattern, rec.email):
                raise ValidationError(_("Format E-mail tidak valid."))

    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active

    def name_get(self):
        res = []
        for r in self:
            label_parts = []
            if r.no_rm:
                label_parts.append(r.no_rm)
            if r.name:
                label_parts.append(r.name)
            res.append((r.id, " | ".join(label_parts) or r.display_name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        args = args or []
        if not name:
            recs = self.search(args, limit=limit)
            return recs.name_get()
        domain = ['|','|','|',
                  ('no_rm', operator, name),
                  ('name', operator, name),
                  ('no_identitas', operator, name),
                  ('phone', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def _compute_emr_status_pelayanan(self):
        Kunj = self.env['pfn.kunjungan.pasien']
        fdef = Kunj.fields_get(['status_pelayanan'])['status_pelayanan']
        sel_map = dict(fdef.get('selection', []))
        for rec in self:
            label = False
            dom_base = [('patient_id', '=', rec.id), ('status_kunjungan', '=', 'registered')]
            kunj = Kunj.search(
                dom_base + [
                    ('doctor_id.user_id', '=', self.env.user.id),
                    ('status_pelayanan', 'in', ['not_served', 'in_service'])
                ],
                order='visit_datetime desc', limit=1
            )
            if not kunj:
                kunj = Kunj.search(dom_base, order='visit_datetime desc', limit=1)
            if kunj:
                label = sel_map.get(kunj.status_pelayanan, kunj.status_pelayanan or False)
            rec.emr_status_pelayanan = label

    def action_open_emr(self):
        """Ambil pasien -> set status pelayanan 'in_service' & buka/buat EMR."""
        self.ensure_one()
        Kunj = self.env['pfn.kunjungan.pasien']
        user = self.env.user

        kunj = Kunj.search([
            ('patient_id', '=', self.id),
            ('status_kunjungan', '=', 'registered'),
            ('status_pelayanan', 'in', ['not_served', 'in_service']),
            ('doctor_id.user_id', '=', user.id),
        ], order='visit_datetime desc', limit=1)

        if not kunj:
            kunj = Kunj.search([
                ('patient_id', '=', self.id),
                ('status_kunjungan', '=', 'registered'),
            ], order='visit_datetime desc', limit=1)

        if not kunj:
            raise UserError(_("Tidak ada kunjungan aktif (registered) untuk pasien ini."))

        if kunj.status_pelayanan != 'in_service':
            kunj.write({'status_pelayanan': 'in_service'})

        Emr = self.env['emr.record']
        emr = Emr.search([('kunjungan_id', '=', kunj.id)], limit=1)
        if not emr:
            emr = Emr.create({
                # NOTE: patient_id TIDAK diisi (related & readonly di emr.record)
                'kunjungan_id': kunj.id,
                'doctor_id': kunj.doctor_id.id if kunj.doctor_id else False,
            })

        action = self.env.ref('clinic_odoo.emr_record_action').read()[0]
        action.update({
            'view_mode': 'form',
            'res_id': emr.id,
            'context': {
                'default_kunjungan_id': kunj.id,
                'default_doctor_id': kunj.doctor_id.id if kunj.doctor_id else False,
            },
        })
        return action


# =========================
#   KUNJUNGAN PASIEN
# =========================
class pfn_kunjungan_pasien(models.Model):
    _name = 'pfn.kunjungan.pasien'
    _description = 'Kunjungan Pasien'
    _rec_name = 'no_reg'
    _order = 'visit_datetime desc, id desc'

    # Pasien
    no_rm_input = fields.Char(
        string='No. RM (Cari)',
        help='Ketik No. RM atau Nama lalu Enter untuk memuat data pasien'
    )
    patient_id = fields.Many2one('pfn.data.pasien', string='Pasien', ondelete='restrict', index=True)

    no_rm         = fields.Char(related='patient_id.no_rm', string='No. RM', store=True, readonly=True)
    name          = fields.Char(related='patient_id.name', string='Nama Lengkap', store=True, readonly=True)
    no_identitas  = fields.Char(related='patient_id.no_identitas', string='No. KTP', store=True, readonly=True)
    tempat_lahir  = fields.Char(related='patient_id.tempat_lahir', string='Tempat Lahir', store=True, readonly=True)
    tanggal_lahir = fields.Date(related='patient_id.tanggal_lahir', string='Tanggal Lahir', store=True, readonly=True)
    umur_display  = fields.Char(related='patient_id.umur_display', string='Umur', store=True, readonly=True)
    gender        = fields.Selection(related='patient_id.gender', string='Jenis Kelamin', store=True, readonly=True)
    phone         = fields.Char(related='patient_id.phone', string='HP', store=True, readonly=True)
    email         = fields.Char(related='patient_id.email', string='E-mail', store=True, readonly=True)
    alamat        = fields.Char(related='patient_id.alamat', string='Alamat', store=True, readonly=True)

    # Registrasi
    no_reg = fields.Char(string='No. Registrasi', readonly=True, copy=False, index=True)

    service_type_id = fields.Many2one('mst.service.types', string='Jenis Pelayanan', ondelete='restrict', index=True)
    poli_id = fields.Many2one(
        'mst.poli', string='Poli', ondelete='restrict', index=True,
        domain="[('service_type_id','=',service_type_id)]"
    )
    divisi_id = fields.Many2one(
        'mst.divisi', string='Divisi', ondelete='restrict', index=True,
        domain="[('poli_id','=',poli_id)]"
    )

    visit_datetime = fields.Datetime(
        string='Tanggal & Jam Kunjungan',
        default=lambda self: fields.Datetime.now(),
        required=True
    )
    visit_date = fields.Date(string='Tanggal (hari)',
                             compute='_compute_visit_date', store=True, index=True)

    doctor_id = fields.Many2one(
        'hr.employee', string='Dokter Pemeriksa', ondelete='restrict', index=True,
        domain="[('id','in', available_doctor_ids)]"
    )
    available_doctor_ids = fields.Many2many(
        'hr.employee', compute='_compute_available_doctor_ids',
        string='Dokter Tersedia', store=False
    )

    queue_no = fields.Integer(string='Nomor Antrian', readonly=True)

    status_kunjungan = fields.Selection([
        ('registered', 'Teregistrasi'),
        ('cancel', 'Batal Kunjungan'),
        ('done', 'Selesai (Bayar)'),
    ], string='Status Kunjungan', default='registered', required=True, index=True)

    status_pelayanan = fields.Selection([
        ('not_served', 'Belum Dilayani'),
        ('in_service', 'Dalam Pelayanan'),
        ('finished', 'Selesai'),
        ('verified', 'Sudah Verifikasi'),
    ], string='Status Pelayanan', default='not_served', required=True, index=True)

    state = fields.Selection(related='status_pelayanan', string='Status', store=False)

    emr_id = fields.Many2one('emr.record', string='EMR', readonly=True, copy=False)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('pfn_no_reg_unique', 'unique(no_reg)', 'Nomor Registrasi harus unik!'),
        ('unique_queue_per_doctor_day',
         'unique(doctor_id, visit_date, queue_no)',
         'Nomor antrian harus unik untuk dokter pada tanggal yang sama!'),
    ]

    # ---------- computes / onchange ----------
    @api.depends('visit_datetime')
    def _compute_visit_date(self):
        for rec in self:
            rec.visit_date = fields.Date.to_date(rec.visit_datetime) if rec.visit_datetime else False

    @api.onchange('no_rm_input')
    def _onchange_no_rm_input(self):
        txt = (self.no_rm_input or '').strip()
        if not txt:
            self.patient_id = False
            return
        patient = self.env['pfn.data.pasien'].search(
            ['|', ('no_rm', '=', txt), ('name', 'ilike', txt)],
            limit=1
        )
        self.patient_id = patient or False

    @api.depends('service_type_id', 'poli_id', 'divisi_id')
    def _compute_available_doctor_ids(self):
        Map = self.env['mst.unit.pelayanan.dokter']
        for rec in self:
            domain = [('active', '=', True)]
            if rec.divisi_id:
                domain.append(('divisi_id', '=', rec.divisi_id.id))
            elif rec.poli_id:
                domain.append(('poli_id', '=', rec.poli_id.id))
            elif rec.service_type_id:
                domain.append(('service_type_id', '=', rec.service_type_id.id))
            else:
                rec.available_doctor_ids = [(6, 0, [])]
                continue
            maps = Map.search(domain)
            rec.available_doctor_ids = [(6, 0, maps.mapped('employee_id').ids)]

    @api.onchange('service_type_id')
    def _onchange_service_type(self):
        if self.service_type_id and self.poli_id and self.poli_id.service_type_id != self.service_type_id:
            self.poli_id = False
            self.divisi_id = False
            self.doctor_id = False

    @api.onchange('poli_id')
    def _onchange_poli(self):
        if self.poli_id and self.divisi_id and self.divisi_id.poli_id != self.poli_id:
            self.divisi_id = False
            self.doctor_id = False

    @api.onchange('doctor_id', 'visit_datetime')
    def _onchange_queue_no(self):
        if self.doctor_id:
            vdt = self.visit_datetime or fields.Datetime.now()
            self.queue_no = self._next_queue_no(self.doctor_id.id, vdt)
        else:
            self.queue_no = 0

    # ---------- actions ----------
    def action_open_create_patient(self):
        action = self.env.ref('clinic_odoo.pfn_data_pasien_action').read()[0]
        action.update({'view_mode': 'form', 'target': 'new', 'context': {'default_no_rm': False}})
        return action

    # ---------- helpers ----------
    def _next_queue_no(self, doctor_id, visit_dt):
        if not doctor_id or not visit_dt:
            return 0
        the_date = fields.Date.to_date(visit_dt)
        last = self.search([
            ('doctor_id', '=', doctor_id),
            ('visit_date', '=', the_date),
        ], order='queue_no desc', limit=1)
        return (last.queue_no or 0) + 1

    # ---------- overrides ----------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # visit_date
            vdt = vals.get('visit_datetime') or fields.Datetime.now()
            vals.setdefault('visit_date', fields.Date.to_date(vdt))

            # queue_no bila ada dokter
            if vals.get('doctor_id') and not vals.get('queue_no'):
                vals['queue_no'] = self._next_queue_no(vals['doctor_id'], vdt)

            # nomor registrasi
            if not vals.get('no_reg'):
                poli = self.env['mst.poli'].browse(vals.get('poli_id')) if vals.get('poli_id') else False
                if not poli:
                    raise UserError(_('Pilih Poli terlebih dahulu untuk membuat Nomor Registrasi.'))

                visit_dt = fields.Datetime.to_datetime(vdt)
                ym = visit_dt.strftime('%Y%m')

                seq = self.env['ir.sequence']\
                    .with_context(ir_sequence_date=visit_dt.date())\
                    .next_by_code('pfn.kunjungan.monthly') or '0'
                seq = str(seq).zfill(4)

                visit_index = 1
                if vals.get('patient_id'):
                    # hitung kunjungan pasien pada bulan yang sama
                    start = visit_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end = start + relativedelta(months=1)
                    count = self.search_count([
                        ('patient_id', '=', vals['patient_id']),
                        ('visit_datetime', '>=', start),
                        ('visit_datetime', '<', end),
                    ])
                    visit_index = count + 1
                visit_index_str = str(visit_index).zfill(3)

                kode_poli = (poli.kode or '').zfill(4)
                vals['no_reg'] = f"{kode_poli}{ym}{seq}{visit_index_str}"

        return super().create(vals_list)

    def write(self, vals):
        for rec in self:
            updates = dict(vals)

            # sinkron visit_date bila visit_datetime diubah
            vdt = updates.get('visit_datetime', rec.visit_datetime)
            if 'visit_datetime' in updates:
                updates['visit_date'] = fields.Date.to_date(vdt) if vdt else False

            # kalau dokter/tanggal berubah → hitung ulang antrian
            if 'doctor_id' in updates or 'visit_datetime' in updates:
                doctor_id = updates.get('doctor_id', rec.doctor_id.id)
                if doctor_id:
                    updates['queue_no'] = rec._next_queue_no(doctor_id, vdt or fields.Datetime.now())
                else:
                    updates['queue_no'] = 0

            super(pfn_kunjungan_pasien, rec).write(updates)
        return True

    def _get_or_create_emr(self):
        self.ensure_one()
        emr = self.emr_id
        if not emr:
            emr = self.env['emr.record'].create({
                'kunjungan_id': self.id,
                # name otomatis ikut no_reg di emr.record (related)
            })
            self.emr_id = emr.id
        return emr

    def action_take_patient(self):
        """Dipakai dari tombol 'Ambil Pasien' di tree EMR."""
        for rec in self:
            if rec.status_pelayanan in ('finished', 'verified'):
                raise UserError(_('Kunjungan sudah selesai/terverifikasi.'))
            rec.status_pelayanan = 'in_service'
            emr = rec._get_or_create_emr()
            action = self.env.ref('clinic_odoo.emr_record_action').read()[0]
            action['res_id'] = emr.id
            return action
