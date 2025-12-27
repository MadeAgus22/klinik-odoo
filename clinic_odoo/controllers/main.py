# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class ClinicOdontogramController(http.Controller):

    @http.route('/clinic_odoo/save_odontogram', type='json', auth='user')
    def save_odontogram(self, emr_id, odontogram_data):
        """
        Menyimpan data odontogram.
        Karena type='json', Odoo akan otomatis mencocokkan isi 'params' dari JS
        ke argumen fungsi ini (emr_id & odontogram_data).
        """
        # 1. Validasi: Pastikan emr_id tidak kosong (None/False)
        if not emr_id:
            return {'success': False, 'error': 'EMR ID is missing (None)'}

        # 2. Validasi: Pastikan emr_id bisa diubah jadi angka (integer)
        try:
            emr_id_int = int(emr_id)
        except (ValueError, TypeError):
            return {'success': False, 'error': f'Invalid EMR ID format: {emr_id}'}

        # 3. Cari record EMR di database
        emr_record = request.env['emr.record'].browse(emr_id_int)
        
        if not emr_record.exists():
            return {'success': False, 'error': 'EMR Record not found in database'}

        # 4. Simpan ke dalam model emr.odontogram (relasi)
        if not emr_record.odontogram_id:
            # Jika belum ada data odontogram, buat baru
            odo = request.env['emr.odontogram'].create({
                'odontogram_data': odontogram_data
            })
            emr_record.odontogram_id = odo.id
        else:
            # Jika sudah ada, update data yang lama
            emr_record.odontogram_id.write({
                'odontogram_data': odontogram_data
            })

        return {'success': True}

    @http.route('/clinic_odoo/get_odontogram', type='json', auth='user')
    def get_odontogram(self, emr_id):
        """ Mengambil data saat loading halaman """
        # Validasi sederhana untuk load data
        if not emr_id:
            return {'data': None}
            
        try:
            emr_id_int = int(emr_id)
        except (ValueError, TypeError):
             return {'data': None}

        emr = request.env['emr.record'].browse(emr_id_int)
        
        # Cek apakah EMR ada dan memiliki data odontogram tersimpan
        if emr.exists() and emr.odontogram_id and emr.odontogram_id.odontogram_data:
            return {'data': emr.odontogram_id.odontogram_data}
            
        return {'data': None}