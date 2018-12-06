# -*- coding: utf-8 -*-
from odoo import http

class GuardsSaleWidget(http.Controller):

    @http.route('/guard_sales_report/document',type='json', auth='user')
    def index(self, **kwargs):
        flag = http.request.env['guards.sale.widget'].create_excel_file(kwargs['bom_id'], kwargs['quantity'], '/tmp/sale_report.xlsx')
        if flag:
            return {'url': '/guards_sales_report/file_download'}
        return

    @http.route('/guards_sales_report/file_download', type='http', auth='user')
    def download_document(self, **kwargs):
        file = open('/tmp/sale_report.xlsx')
        return http.request.make_response(file, headers=[
                ('Content-Type', 'application/octet-stream;charset=utf-8;'),
                ('Content-Disposition', u'attachment; filename=SaleReport.xlsx;')
            ])
