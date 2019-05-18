# -*- coding: utf-8 -*-
from odoo import http

class GuardsBomFormWidget(http.Controller):

    @http.route('/guard_product_bom/document',type='json', auth='user')
    def index(self, **kwargs):
        flag = http.request.env['bom.widget'].create_excel_file(kwargs['bom_id'], kwargs['quantity'], '/tmp/bom_report.xlsx')
        if flag:
            return {'url': '/guards_bom_widget/file_download'}
        return

    @http.route('/guards_bom_widget/file_download', type='http', auth='user')
    def download_document(self, **kwargs):
        file = open('/tmp/bom_report.xlsx')
        return http.request.make_response(file, headers=[
                ('Content-Type', 'application/octet-stream;charset=utf-8;'),
                ('Content-Disposition', u'attachment; filename=Report.xlsx;')
            ])
