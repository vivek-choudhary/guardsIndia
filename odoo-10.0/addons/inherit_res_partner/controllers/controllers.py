# -*- coding: utf-8 -*-
from odoo import http

# class InheritResPartner(http.Controller):
#     @http.route('/inherit_res_partner/inherit_res_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inherit_res_partner/inherit_res_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inherit_res_partner.listing', {
#             'root': '/inherit_res_partner/inherit_res_partner',
#             'objects': http.request.env['inherit_res_partner.inherit_res_partner'].search([]),
#         })

#     @http.route('/inherit_res_partner/inherit_res_partner/objects/<model("inherit_res_partner.inherit_res_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inherit_res_partner.object', {
#             'object': obj
#         })