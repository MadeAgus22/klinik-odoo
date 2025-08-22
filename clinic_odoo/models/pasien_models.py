# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import random
import re


class pfn_data_pasien(models.Model):
    _name = 'pfn.data.pasien'
    _description = 'Pendaftaran - Data Pasien'
    _rec_name = 'name'

    # --- Identitas utama ---
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

    # Umur tampil “XX tahun YY bulan”
    umur_display = fields.Char(
        string='Umur', compute='_compute_umur', store=True, readonly=True)

    gender = fields.Selection(
        [('male', 'Laki-laki'), ('female', 'Perempuan')],
        string='Jenis Kelamin', required=True
    )
    phone = fields.Char(string='Nomer HP', required=True)
    email = fields.Char(string='E-mail', required=True)

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('no_rm_unique', 'unique(no_rm)', 'Nomer Rekam Medis harus unik!'),
        ('no_identitas_unique', 'unique(no_identitas)', 'No. KTP sudah digunakan!'),
    ]

    # ----- Generate No. RM otomatis (YYMM + 4 digit acak) -----
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('no_rm') or vals.get('no_rm') == 'New':
                today = fields.Date.context_today(self)
                yy = f"{today.year % 100:02d}"
                mm = f"{today.month:02d}"
                # cari kombinasi unik
                while True:
                    rand4 = f"{random.randint(0, 9999):04d}"
                    candidate = f"{yy}{mm}{rand4}"
                    if not self.search_count([('no_rm', '=', candidate)]):
                        vals['no_rm'] = candidate
                        break
        return super().create(vals_list)

    # ----- Hitung umur “XX tahun YY bulan” -----
    @api.depends('tanggal_lahir')
    def _compute_umur(self):
        today = date.today()
        for rec in self:
            if rec.tanggal_lahir:
                rd = relativedelta(today, rec.tanggal_lahir)
                rec.umur_display = _("%s tahun %s bulan") % (rd.years, rd.months)
            else:
                rec.umur_display = False

    # ----- Validasi email sederhana -----
    @api.constrains('email')
    def _check_email(self):
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        for rec in self:
            if rec.email and not re.match(pattern, rec.email):
                raise ValidationError(_("Format E-mail tidak valid."))
  
    def action_toggle_active(self):
        for rec in self:
            rec.active = not rec.active




