# -*- coding: utf-8 -*-
from odoo import http

# class GoogleMapsTest(http.Controller):
#     @http.route('/google_maps_test/google_maps_test/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/google_maps_test/google_maps_test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('google_maps_test.listing', {
#             'root': '/google_maps_test/google_maps_test',
#             'objects': http.request.env['google_maps_test.google_maps_test'].search([]),
#         })

#     @http.route('/google_maps_test/google_maps_test/objects/<model("google_maps_test.google_maps_test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('google_maps_test.object', {
#             'object': obj
#         })