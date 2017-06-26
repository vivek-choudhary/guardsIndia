# -*- coding: utf-8 -*-
from odoo import http

# class GuardPayments(http.Controller):
#     @http.route('/guard_payments/guard_payments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/guard_payments/guard_payments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('guard_payments.listing', {
#             'root': '/guard_payments/guard_payments',
#             'objects': http.request.env['guard_payments.guard_payments'].search([]),
#         })

#     @http.route('/guard_payments/guard_payments/objects/<model("guard_payments.guard_payments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('guard_payments.object', {
#             'object': obj
#         })