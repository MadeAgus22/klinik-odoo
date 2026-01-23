# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
import pytz

class SetDoctorsSchedule(models.Model):
    _name = 'set.doctors.schedule'
    _description = 'Setting Jadwal Dokter'
    _rec_name = 'doctor_id'

    # --- Relasi Utama ---
    doctor_id = fields.Many2one('hr.employee', string='Dokter', required=True, index=True)
    unit_pelayanan_id = fields.Many2one('mst.unit.pelayanan.dokter', string='Unit Pelayanan')
    session_id = fields.Many2one('mst.sesi.pelayanan', string='Sesi', required=True)

    # --- Field Input Range (Hanya untuk Form View) ---
    start_date_req = fields.Date(string='Tanggal Mulai', default=fields.Date.context_today, required=True)
    end_date_req = fields.Date(string='Tanggal Akhir', default=fields.Date.context_today, required=True)

    # --- Field Penyimpanan (Per Hari) ---
    schedule_date = fields.Date(string='Tanggal Jadwal', required=True, default=fields.Date.context_today)
    
    # Compute field untuk Kalender (Store=True agar bisa disearch/filter)
    start_datetime = fields.Datetime(string='Waktu Mulai', compute='_compute_datetime', store=True)
    end_datetime = fields.Datetime(string='Waktu Selesai', compute='_compute_datetime', store=True)

    # --- Quota & Perhitungan ---
    quota = fields.Integer(string='Quota Pasien', default=10, required=True)
    average_duration = fields.Float(string='Rata-rata (Menit/Pasien)', compute='_compute_average_duration', store=True)

    # -------------------------------------------------------------------------
    # 1. COMPUTE DATETIME (CORE LOGIC DARI GEMINI AI)
    # -------------------------------------------------------------------------
    @api.depends('schedule_date', 'session_id')
    def _compute_datetime(self):
        for rec in self:
            if rec.schedule_date and rec.session_id:
                # A. Ambil Timezone User (default UTC jika error/kosong)
                try:
                    user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                except Exception:
                    user_tz = pytz.UTC
                
                utc_tz = pytz.UTC

                # B. Helper untuk ambil jam/menit dari master sesi (handle integer/float/char)
                def get_str_time(val):
                    # Ubah ke int dulu biar aman, baru string zfill
                    try:
                        return str(int(val)).zfill(2)
                    except:
                        return '00'

                jam_awal = get_str_time(rec.session_id.awal_jam)
                menit_awal = get_str_time(rec.session_id.awal_menit)
                jam_akhir = get_str_time(rec.session_id.akhir_jam)
                menit_akhir = get_str_time(rec.session_id.akhir_menit)

                # C. Susun String Waktu Lokal (YYYY-MM-DD HH:MM:SS)
                # str(rec.schedule_date) otomatis format YYYY-MM-DD
                start_str = f"{rec.schedule_date} {jam_awal}:{menit_awal}:00"
                end_str = f"{rec.schedule_date} {jam_akhir}:{menit_akhir}:00"

                # D. Ubah string jadi object datetime 'naive' (tanpa timezone dulu)
                try:
                    start_dt_naive = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                    end_dt_naive = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Fallback jika format error
                    rec.start_datetime = False
                    rec.end_datetime = False
                    continue

                # E. LOGIC LINTAS HARI (Overnight Shift)
                # Jika Jam Selesai <= Jam Mulai (misal 08:00 <= 22:00)
                # Berarti selesai di hari berikutnya -> Tambah 1 Hari
                if end_dt_naive <= start_dt_naive:
                    end_dt_naive += timedelta(days=1)

                # F. KONVERSI TIMEZONE (Lokal -> UTC)
                # 1. 'localize': Beritahu Python bahwa waktu ini adalah waktu User (misal WIB)
                start_dt_local = user_tz.localize(start_dt_naive)
                end_dt_local = user_tz.localize(end_dt_naive)

                # 2. 'astimezone': Konversi waktu WIB tadi ke UTC
                start_dt_utc = start_dt_local.astimezone(utc_tz)
                end_dt_utc = end_dt_local.astimezone(utc_tz)

                # 3. Simpan ke Odoo (Hapus info tzinfo karena Odoo database pure UTC naive)
                rec.start_datetime = start_dt_utc.replace(tzinfo=None)
                rec.end_datetime = end_dt_utc.replace(tzinfo=None)
            else:
                rec.start_datetime = False
                rec.end_datetime = False

    # -------------------------------------------------------------------------
    # 2. COMPUTE AVERAGE DURATION
    # -------------------------------------------------------------------------
    @api.depends('start_datetime', 'end_datetime', 'quota')
    def _compute_average_duration(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.quota > 0:
                diff = rec.end_datetime - rec.start_datetime
                duration_minutes = diff.total_seconds() / 60
                rec.average_duration = duration_minutes / rec.quota
            else:
                rec.average_duration = 0.0

    # -------------------------------------------------------------------------
    # 3. CREATE (BULK INSERT DARI FORM RANGE)
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            s_date = vals.get('start_date_req')
            e_date = vals.get('end_date_req')
            
            # Jika user input via Form Pop-up (ada range tanggal)
            if s_date and e_date:
                start_dt = fields.Date.to_date(s_date)
                end_dt = fields.Date.to_date(e_date)

                if start_dt > end_dt:
                    raise ValidationError(_("Tanggal Akhir tidak boleh lebih kecil dari Tanggal Mulai."))

                delta = end_dt - start_dt
                # Loop dari hari pertama sampai hari terakhir
                for i in range(delta.days + 1):
                    current_date = start_dt + timedelta(days=i)
                    
                    # Copy data dasar
                    new_vals = vals.copy()
                    # Paksa schedule_date sesuai loop
                    new_vals['schedule_date'] = current_date
                    
                    # Hapus field dummy agar tidak error (opsional tapi rapi)
                    new_vals.pop('start_date_req', None)
                    new_vals.pop('end_date_req', None)
                    
                    new_vals_list.append(new_vals)
            else:
                # Jika create manual biasa (bukan dari wizard range)
                new_vals_list.append(vals)

        return super(SetDoctorsSchedule, self).create(new_vals_list)

    def name_get(self):
        res = []
        for rec in self:
            date_label = rec.schedule_date.strftime('%d/%m/%Y') if rec.schedule_date else ''
            name = f"{rec.doctor_id.name} ({date_label})"
            res.append((rec.id, name))
        return res