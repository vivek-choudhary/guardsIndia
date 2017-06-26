# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class GuardPaymentInvoiceInterface(models.Model):
    _name = 'guard.interface'
    _description = 'Parent Model'
    _inherit = ['mail.thread']

    amount = fields.Char(string='Amount')
    company = fields.Many2one('res.company', string='Company')
    due_date = fields.Date(string='Due Date', default=fields.Date.today())
    paid_flag = fields.Boolean(string='Payment Flag', track_visibility='onchange')
    overdue_flag = fields.Boolean(string='Overdue Flag', compute="_compute_overdue_date", store=False)
    overdue = fields.Char(store=False, string="Overdue")
    due = fields.Char(store=False, string='Due', compute="_compute_due_date")

    def _compute_overdue_date(self):
        today = datetime.date.today()
        self.overdue_flag=False
        if self.payment_date<today:
            self.overdue_flag=True
            self.overdue = today - self.payment_date

    def _compute_due_date(self):
        today = datetime.date.today()
        if self.payment_date>today:
            self.due = self.payment_date - today


class GuardPayments(models.Model):
    _name = 'guard.payments'
    _inherit = ['guard.interface']

    payment_date = fields.Date(string='Payment Date')
    bill_number = fields.Char(string='Bill Number')
    company = fields.Many2one('res.partner', string="Party Name")


class GuardInvoices(models.Model):
    _name = 'guard.invoices'
    _inherit = ['guard.interface']

    customer = fields.Many2one('res.partner', string='Client')
    sales_person = fields.Many2one('res.partner', string='Sales Person')
    invoice_number = fields.Char(string='Invoice Number')
