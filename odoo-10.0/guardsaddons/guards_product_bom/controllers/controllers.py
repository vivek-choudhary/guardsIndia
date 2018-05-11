# -*- coding: utf-8 -*-
from odoo import http

# class GuardsProductBom(http.Controller):
#     @http.route('/guards_product_bom/guards_product_bom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/guards_product_bom/guards_product_bom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('guards_product_bom.listing', {
#             'root': '/guards_product_bom/guards_product_bom',
#             'objects': http.request.env['guards_product_bom.guards_product_bom'].search([]),
#         })

#     @http.route('/guards_product_bom/guards_product_bom/objects/<model("guards_product_bom.guards_product_bom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('guards_product_bom.object', {
#             'object': obj
#         })