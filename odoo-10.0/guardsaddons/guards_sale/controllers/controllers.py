# -*- coding: utf-8 -*-
from odoo import http

# class GuardsSale(http.Controller):
#     @http.route('/guards_sale/guards_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/guards_sale/guards_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('guards_sale.listing', {
#             'root': '/guards_sale/guards_sale',
#             'objects': http.request.env['guards_sale.guards_sale'].search([]),
#         })

#     @http.route('/guards_sale/guards_sale/objects/<model("guards_sale.guards_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('guards_sale.object', {
#             'object': obj
#         })