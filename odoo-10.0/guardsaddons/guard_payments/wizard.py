# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.wizard'

    purchase_ids = fields.Many2many('guard.payments', string='Purchase Ids')
    from_date = fields.Date(string = 'From Date')
    to_date = fields.Date(string = 'To Date')