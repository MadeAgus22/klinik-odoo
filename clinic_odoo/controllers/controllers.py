# -*- coding: utf-8 -*-
# from odoo import http


# class ClinicOdoo(http.Controller):
#     @http.route('/clinic_odoo/clinic_odoo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clinic_odoo/clinic_odoo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('clinic_odoo.listing', {
#             'root': '/clinic_odoo/clinic_odoo',
#             'objects': http.request.env['clinic_odoo.clinic_odoo'].search([]),
#         })

#     @http.route('/clinic_odoo/clinic_odoo/objects/<model("clinic_odoo.clinic_odoo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clinic_odoo.object', {
#             'object': obj
#         })

