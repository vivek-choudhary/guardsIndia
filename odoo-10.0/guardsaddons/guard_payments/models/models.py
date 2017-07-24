# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class GuardPaymentInvoiceInterface(models.Model):
    _name = 'guard.interface'
    _description = 'Parent Model'
    _inherit = ['mail.thread']

    amount = fields.Float(string='Amount')
    company = fields.Many2one('res.company', string='Company')
    due_date = fields.Date(string='Due Date', default=fields.Date.today())
    paid_flag = fields.Boolean(string='Payment Flag', track_visibility='onchange', default=False)
    overdue_flag = fields.Boolean(string='Overdue Flag', compute="_compute_overdue_date", store=False)
    overdue = fields.Char(store=False, string="Overdue")
    due = fields.Char(store=False, string='Due', compute="_compute_due_date")


class GuardPayments(models.Model):
    _name = 'guard.payments'
    _inherit = ['guard.interface']

    payment_date = fields.Date(string='Payment Date', default=fields.Date.today())
    bill_number = fields.Char(string='Bill Number')
    company = fields.Many2one('res.partner', string="Party Name", domain=[('is_company','=',True)])

    def _compute_overdue_date(self):
        for record in self:
            if record.overdue_flag:
                continue
            flag,overdue = self._get_overdue_value(record)
            record.overdue_flag=flag
            if overdue:
                record.overdue = '%s Days(s)' % overdue.days

    def _get_overdue_value(self, record):
        flag = False
        today = datetime.today()
        overdue = None
        due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
        if due_date < today:
            flag=True
            overdue = today - due_date

        return flag,overdue

    def _compute_due_date(self):
        for record in self:
            record.due = '%s Day(s)'%self._get_due_date(record).days

    def _get_due_date(self, record):
        today = datetime.today()
        due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
        if due_date > today:
            return due_date - today

    @api.one
    def register_payment(self):
        self.paid_flag = True
        self.payment_date = fields.Date.today()

    def _update_due_date(self):
        all_ids = self.search([]).ids
        records = self.browse(all_ids)
        for record in records:
            if not record.overdue_flag:
                record.write({'due': '%s Day(s)' % self._get_due_date(record).days})
        return

    def _update_overdue_date(self):
        all_ids = self.search([]).ids
        records = self.browse(all_ids)
        for record in records:
            flag, overdue = self._get_overdue_value(record)
            if overdue:
                record.write({'overdue': '%s Day(s)' % overdue.days, 'overdue_flag': flag})


class GuardInvoices(models.Model):
    _name = 'guard.invoices'
    _inherit = ['guard.interface']

    customer = fields.Many2one('res.partner', string='Client')
    sales_person = fields.Many2one('res.partner', string='Sales Person', domain=[('is_company','=',False)])
    invoice_number = fields.Char(string='Invoice Number')

    @api.one
    def register_payment(self):
        self.paid_flag = True
        self.payment_date = fields.Date.today()

    def _compute_overdue_date(self):
        today = datetime.today()
        for record in self:
            if record.overdue_flag:
                continue
            record.overdue_flag=False
            due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
            if due_date < today:
                record.overdue_flag=True
                record.overdue = today - due_date

    def _compute_due_date(self):
        today = datetime.today()
        for record in self:
            due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
            if due_date > today:
                record.due = due_date - today