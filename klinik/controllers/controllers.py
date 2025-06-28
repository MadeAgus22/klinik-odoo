# -*- coding: utf-8 -*-
# from odoo import http


# class Klinik(http.Controller):
#     @http.route('/klinik/klinik', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/klinik/klinik/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('klinik.listing', {
#             'root': '/klinik/klinik',
#             'objects': http.request.env['klinik.klinik'].search([]),
#         })

#     @http.route('/klinik/klinik/objects/<model("klinik.klinik"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('klinik.object', {
#             'object': obj
#         })

