# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class GuardPaymentInvoiceInterface(models.Model):
  _name = 'guard.interface'
  _description = 'Parent Model'

  amount = fields.Float(string='Amount')
  company = fields.Many2one('res.company')
  due_date = fields.Date(string='Due Date', default=fields.Date.today())
  paid_flag = fields.Boolean(string='Payment Flag', default=False)
  overdue = fields.Char(string="Overdue")
  due = fields.Char(store=False, string='Due', compute="_compute_due_date")
  comment = fields.Text(string='Comments')

  def _compute_due_date(self):
    self.due = (datetime.strptime(self.due_date, '%Y-%m-%d') - datetime.today()).days

  def create_excel_report(self, file_name, field_names, field_display_names, report_data):
    import xlsxwriter

    workbook = xlsxwriter.Workbook(file_name)
    bold = workbook.add_format({'bold': True})
    worksheet = workbook.add_worksheet()

    # Creating Heading Columns
    worksheet.write_row('A1', field_display_names, bold)

    row = 1
    for data in report_data:
      col = 0
      for field in field_names:
        if isinstance(data[field], tuple):
          worksheet.write(row, col, data[field][1])
        else:
          worksheet.write(row, col, data[field])
        col += 1
      row += 1

    workbook.close()

    return file_name


class GuardPayments(models.Model):
  _name = 'guard.payments'
  _description = "Purchase Payments Module"
  _inherits = {'guard.interface': 'interface_id'}
  _rec_name = 'bill_number'

  _sql_constraints = [
        ('bill_number',
         'UNIQUE (bill_number, party_company)',
         'Bill with Seller Company number must be unique!')]

  payment_date = fields.Date(string='Payment Date')
  bill_number = fields.Char(string='Bill Number')
  bill_date = fields.Date(string='Bill Date', default=fields.Date.today())
  due_days = fields.Integer(string='Due Days')
  party_company = fields.Many2one('res.partner', domain="[('is_company','=',True)]", string='Seller Company')
  overdue_flag = fields.Boolean(string='Overdue Flag', compute="_compute_overdue_date", store=False)

  def _compute_overdue_date(self):
    for record in self:
      flag, overdue = self._get_overdue_value(record)
      record.overdue_flag=flag
      if flag:
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
      resp = self._get_due_date(record)
      if resp:
        record.due = '%s Day(s)'%self._get_due_date(record).days

  def _get_due_date(self, record):
    today = datetime.today()
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if due_date > today:
      return due_date - today

  @api.onchange('due_days','bill_date')
  def _compute_due_date(self):
    if not (self.bill_date or self.due_days): return
    self.due_date = (datetime.strptime(self.bill_date, '%Y-%m-%d') + timedelta(days=abs(self.due_days))).date()
    self._compute_overdue_date()

  @api.onchange('due_date')
  def _onchange(self):
    self._compute_overdue_date()

  @api.one
  def register_payment(self):
    self.paid_flag = True
    self.payment_date = fields.Date.today()

  def _update_date(self):
    '''
    Cron function to update dates/ days and send mail to purchase mail ids
    '''
    records = self.search([])
    overdue_records = []
    current_week_due_records= []
    next_week_due_records= []

    for record in records:
      flag, overdue = self._get_overdue_value(record)
      due_resp = self._get_due_date(record)
      if overdue:
        record.write({'overdue': '%s Day(s)' % overdue.days, 'overdue_flag': flag})
        overdue_records.append(record)
      if due_resp and due_resp.days < 7:
        current_week_due_records.append(record)
      elif due_resp and (due_resp.days > 7  and due_resp.days < 14):
        next_week_due_records.append(record)

    context = {'overdue_records': overdue_records,
               'next_week_due_records': next_week_due_records,
               'current_week_due_records': current_week_due_records}
    self.send_mail('guard_payments.mail_payments', self.get_mail_list(), context)
    return

  def get_mail_list(self):
    group_obj = self.env['guard.mail_group'].search([('name','=','Purchase')])[0]
    mail_ids = list(map(lambda a: a.name, group_obj.email_ids))

    return mail_ids

  def send_mail(self, template=None, mail_list=None, context=None):
    template_obj = self.env.ref(template)
    template_obj.email_to = ','.join(mail_list)
    template_obj.email_from = 'Server'
    try:
      template_obj.with_context(context=context).send_mail(self.sudo().id)
    except Exception as ex:
      print ex
    return


  def create_excel_sheet(self, date=None):
    if not date:
      return False

    field_names = ['bill_number','bill_date', 'party_company', 'amount', 'due_days', 'overdue']
    field_display_names = ['Bill Number', 'Bill Date', 'Seller Company', 'Amount', 'Due Days', 'Overdue Days']
    guard_data = self.search_read([('bill_date', '>', date['from']), ('bill_date', '<=', date['to']),('paid_flag','=',False)], field_names)

    file_name = self.env['guard.interface'].create_excel_report('/tmp/report.xlsx', field_names, field_display_names ,guard_data)
    return file_name


class GuardInvoices(models.Model):
  _name = 'guard.invoices'
  _description = 'Sales Invoice Module'
  _inherits = {'guard.interface': 'interface_id'}
  _rec_name = 'invoice_number'
  _sql_constraints = [
        ('invoice_number',
         'UNIQUE (invoice_number, customer)',
         'Bill with Seller Company number must be unique!')]

  customer = fields.Many2one('res.partner', string='Client')
  sales_person = fields.Many2one('res.partner', string='Sales Person', domain=[('is_company','=',False)])
  invoice_number = fields.Char(string='Invoice Number')
  invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today())
  payment_due = fields.Integer(string='Payment Due(days)')
  payment_date = fields.Date(string='Payment Date')
  overdue_flag = fields.Boolean(string='Overdue Flag', compute="_compute_overdue_date", store=False)

  @api.one
  def register_payment(self):
    self.paid_flag = True
    self.payment_date = fields.Date.today()

  @api.onchange('payment_due')
  def _onchange_payment_date(self):
    if self.invoice_date:
      self.due_date = datetime.strptime(self.invoice_date, '%Y-%m-%d') + timedelta(days=abs(self.payment_due))
      self._compute_overdue_date()

  @api.onchange('due_date')
  def _onchange(self):
    self._compute_overdue_date()

  def _compute_overdue_date(self):
    today = datetime.today()
    for record in self:
      flag, overdue = self._get_overdue_value(record)
      record.overdue_flag=flag
      if overdue:
        record.overdue = '%s Days(s)' % overdue.days

  def _compute_due_date(self):
    today = datetime.today()
    for record in self:
      due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
      if due_date > today:
        record.due = due_date - today

  def _get_due_date(self, record):
    today = datetime.today()
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if due_date > today:
      return due_date - today

  def _get_overdue_value(self, record):
    flag = False
    today = datetime.today()
    overdue = None
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if due_date < today:
      flag=True
      overdue = today - due_date

    return flag,overdue

  def _update_date(self):
    records = self.search([])
    overdue_invoices = []
    due_invoices = []
    customer_data = {}

    for record in records:
      flag, overdue = self._get_overdue_value(record)
      due_resp = self._get_due_date(record)
      customer_emails = self._get_customer_email_list(record)

      obj = {}

      if not record.customer.id in customer_data:
        obj['mail_to'] = customer_emails[0]
        obj['mail_cc'] = ''.join(customer_emails[1:len(customer_emails)])

      # record.customer.id
      # record.sales_person.id



      if overdue:
        record.write({'overdue': '%s Day(s)' % overdue.days, 'overdue_flag': flag})
        overdue_invoices.append(record)
        overdue_context = {'record': record}
        self.send_mail('guard_payments.overdue_customer_mail', customer_emails ,overdue_context)
        self.send_mail('guard_payments.saleperson_mail', [record.sales_person.email] ,overdue_context)

      if due_resp:
        due_days = self._get_due_date(record).days
        record.write({'due': '%s Day(s)' % due_days})
        due_context = {'record': record}
        due_invoices.append(record)
        if due_days < 7:
          self.send_mail('guard_payments.due_customer_mail', customer_emails ,due_context)
          self.send_mail('guard_payments.saleperson_mail', [record.sales_person.email] ,due_context)


    context = {'overdue_records': overdue_invoices, 'due_records': due_invoices}
    self.send_mail('guard_payments.overdue_mail_invoices', self.get_mail_list(), context)
    self.send_mail('guard_payments.due_mail_i nvoices', self.get_mail_list(), context)


  def _get_customer_email_list(self, record):
    email = []
    email.append(record.customer.email)
    if record.customer.email_second: email.append(record.customer.email_second)
    if record.customer.email_third: email.append(record.customer.email_third)
    if record.customer.email_fourth: email.append(record.customer.email_fourth)
    return  email

  def create_excel_sheet(self, date=None):
    if not date:
      return False

    field_names = ['invoice_number', 'invoice_date', 'customer', 'amount', 'payment_due', 'overdue']
    field_display_names = ['Invoice Number', 'Invoice Date', 'Customer', 'Amount', 'Due Days', 'Overdue Days']
    guard_data = self.search_read([('invoice_date', '>', date['from']), ('invoice_date', '<=', date['to']), ('paid_flag','=',False)], field_names)

    file_name = self.env['guard.interface'].create_excel_report('/tmp/report.xlsx', field_names, field_display_names, guard_data)
    return file_name

  def get_mail_list(self):
    '''

    :return: List of emails in Sales Group
    '''
    group_obj = self.env['guard.mail_group'].search([('name','=','Sales')])[0]
    mail_ids = list(map(lambda a: a.name, group_obj.email_ids))

    return mail_ids

  def send_mail(self, template=None, mail_list=None, context=None):
    if not len(mail_list):
      return
    template_obj = self.env.ref(template)
    template_obj.email_to = ','.join(mail_list)
    template_obj.email_from = 'Server'
    try:
      template_obj.with_context(context=context).send_mail(self.sudo().id)
    except Exception as ex:
      print ex
    return



class ResPartner(models.Model):
  _name='res.partner'
  _inherit='res.partner'

  email_second = fields.Char(string='Second Email')
  email_third = fields.Char(string='Third Email')
  email_fourth = fields.Char(string='Fourth Email')

