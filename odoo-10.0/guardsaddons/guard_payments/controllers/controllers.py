# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

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

class GuardPayments(http.Controller):

  @http.route('/guard_payments/document', type='json', auth='user')
  def download_document(self, **kwargs):

    if kwargs['type'] == 'purchase':
      obj = http.request.env['guard.payments']
    elif kwargs['type'] == 'sale':
      obj = http.request.env['guard.invoices']

    flag = obj.create_excel_sheet(data={'from': kwargs['from_date'], 'to': kwargs['to_date'],
                                        'company_id': kwargs['company_id']})

    if flag:
      return {'url': '/guard_payments/get_file'}
    return

  @http.route('/guard_payments/get_file', type='http', auth='user')
  def get_file(self, **kwargs):
    file = open('/tmp/report.xlsx')
    return request.make_response(file, headers=[
            ('Content-Type', 'application/octet-stream;charset=utf-8;'),
            ('Content-Disposition', u'attachment; filename=Report.xlsx;')
        ])
