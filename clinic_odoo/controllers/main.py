from odoo import http
from odoo.http import request  # impor objek request yang benar

class ClinicOdontogramController(http.Controller):

    @http.route('/clinic_odoo/save_odontogram', type='json', auth='user', methods=['POST'])
    def save_odontogram(self):
        """
        Menerima payload JSON dengan struktur {'emr_id': ..., 'data': ...}
        lalu menyimpan ke kolom odontogram_data.
        """
        payload = request.jsonrequest  # dapatkan dict dari body JSON
        emr_id = payload.get('emr_id')
        data = payload.get('data')
        if not emr_id:
            return {'success': False, 'error': 'Missing emr_id'}

        emr_record = request.env['emr.record'].sudo().browse(int(emr_id))
        if not emr_record:
            return {'success': False, 'error': 'EMR not found'}

        emr_record.write({'odontogram_data': data})
        return {'success': True}
