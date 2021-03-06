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
  due = fields.Integer(store=False, string='Due', compute="_compute_due_date")
  comment = fields.Text(string='Comments')
  overdue_reminders = fields.Integer(string='Overdue Reminders')

  def _compute_due_date(self):
    for record in self:
      record.due = (datetime.strptime(record.due_date, '%Y-%m-%d') - datetime.today()).days

  def create_excel_report(self, file_name, field_names, field_display_names, report_data, model=None):
    import xlsxwriter

    workbook = xlsxwriter.Workbook(file_name)
    bold = workbook.add_format({'bold': True})
    date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
    worksheet = workbook.add_worksheet()

    # Creating Heading Columns
    worksheet.write_row('A1', field_display_names, bold)

    row = 1
    for data in report_data:
      col = 0
      for field in field_names:
        if isinstance(data[field], tuple):
          worksheet.write(row, col, data[field][1])
        elif isinstance(data[field], bool):
          worksheet.write(row, col, 'Yes' if data[field] else 'No')
        elif self.env['ir.model.fields'].search([('name','=',field),('model','=',model)]).ttype == 'date':
          date_value = datetime.strptime(data[field],'%Y-%m-%d').date()
          worksheet.write(row, col,date_value if date_value else '', date_format)
        else:
          worksheet.write(row, col, data[field] if data[field] else ' ')
        col += 1
      row += 1

    workbook.close()

    return file_name


class GuardPayments(models.Model):
  _name = 'guard.payments'
  _description = "Purchase Payments Module"
  _inherits = {'guard.interface': 'interface_id'}
  _rec_name = 'bill_number'
  _order = 'paid_flag asc, due_date asc'

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
  actual_amount = fields.Text(string='Actual Amount')

  @api.one
  def un_register_payment(self):
    self.payment_date = None
    self.paid_flag = False

  def _compute_overdue_date(self):
    for record in self:
      flag, overdue = self._get_overdue_value(record)
      record.overdue_flag = flag
      if flag:
        record.overdue = '%s Days(s)' % (overdue.days if overdue.days > 0 else 0)
    return True

  def _get_overdue_value(self, record):
    flag = False
    today = datetime.today()
    overdue = None
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if record.paid_flag:
      today = datetime.strptime(record.payment_date, '%Y-%m-%d')
    if due_date < today or record.overdue > 0 :
      overdue = today - due_date
      flag = True

    return flag,overdue

  def _compute_due_date(self):
    for record in self:
      resp = self._get_due_date(record)
      if resp:
        record.due = '%s Day(s)'%resp.days

  def _get_due_date(self, record):
    today = datetime.today()
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if due_date > today:
      return due_date - today

  @api.onchange('due_date','due_days','bill_date')
  def _compute_due_date_onchange(self):
    if not (self.bill_date or self.due_days): return
    self.due_date = (datetime.strptime(self.bill_date, '%Y-%m-%d') + timedelta(days=self.due_days)).date()
    self._compute_overdue_date()
    resp = self._get_due_date(self)
    if resp:
      self.due = resp.days
    else:
      self.due = 0

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
      if record.payment_date or record.paid_flag: continue
      overdue_flag, overdue = self._get_overdue_value(record)
      due_resp = self._get_due_date(record)
      if overdue:
        record.write({'overdue': '%s Day(s)' % overdue.days, 'overdue_flag': overdue_flag})
        overdue_records.append(record) if overdue.days > 0 else False
      if due_resp and due_resp.days < 7:
        current_week_due_records.append(record)
      elif due_resp and (due_resp.days > 7  and due_resp.days < 14):
        next_week_due_records.append(record)

    context = {'overdue_records': overdue_records,
               'next_week_due_records': next_week_due_records,
               'current_week_due_records': current_week_due_records}
    if len(overdue_records) or len(next_week_due_records) or len(current_week_due_records):
      self.send_mail('guard_payments.mail_payments', self.get_mail_list(), context)
    return

  def get_mail_list(self):
    group_obj = self.env['guard.mail_group'].search([('name','=','Purchase')])[0]
    mail_ids = list(map(lambda a: a.name, group_obj.email_ids))

    return mail_ids

  def send_mail(self, template=None, mail_list=None, context=None):
    template_obj = self.env.ref(template)
    template_obj.email_to = ','.join(mail_list)
    try:
      template_obj.with_context(context=context).send_mail(self.sudo().id)
    except Exception as ex:
      print ex
    return


  def create_excel_sheet(self, data=None):
    if not data:
      return False

    field_names = ['bill_number','bill_date', 'party_company', 'amount', 'due_days', 'overdue','paid_flag','payment_date','overdue_flag', 'due']
    field_display_data = ['bill_number','bill_date', 'party_company', 'amount', 'due_days', 'overdue','paid_flag','payment_date']
    field_display_names = ['Bill Number', 'Bill Date', 'Seller Company', 'Amount', 'Payment Terms', 'Overdue Days', 'Paid', 'Payment Date']

    filter_arr = ['|', ('due_date','<=',fields.Date.today()),('due_date', '>', data['from']), ('due_date', '<=', data['to'])]
    if data['company_id']:
      filter_arr.append(('party_company','=',int(data['company_id'])))

    guard_data = self.search_read(filter_arr, field_names)

    file_name = self.env['guard.interface'].create_excel_report('/tmp/report.xlsx', field_display_data, field_display_names ,
                                                                sorted(guard_data, key=lambda x: x['due']), model='guard.payments')
    return file_name


class GuardInvoices(models.Model):
  _name = 'guard.invoices'
  _description = 'Sales Invoice Module'
  _inherits = {'guard.interface': 'interface_id'}
  _rec_name = 'invoice_number'
  _order = 'paid_flag asc, due_date asc'
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
  actual_amount = fields.Text(string='Actual Amount')

  @api.one
  def register_payment(self):
    self.paid_flag = True
    self.payment_date = fields.Date.today()

  @api.one
  def un_register_payment(self):
    self.payment_date = None
    self.paid_flag = False

  @api.onchange('payment_due','due_date')
  def _onchange_payment_date(self):
    if self.invoice_date:
      self.due_date = datetime.strptime(self.invoice_date, '%Y-%m-%d') + timedelta(days=self.payment_due)
      self._compute_overdue_date()
      resp = self._get_due_date(self)
      if resp:
        self.due = resp.days
      else:
        self.due = 0

  def _compute_overdue_date(self):
    today = datetime.today()
    for record in self:
      flag, overdue = self._get_overdue_value(record)
      record.overdue_flag=flag
      if overdue:
        record.overdue = '%s Days(s)' % overdue.days
      else:
        record.overdue = '0 Day(s)'

  def _compute_due_date(self):
    today = datetime.today()
    for record in self:
      due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
      if due_date > today:
        record.due = due_date - today

  def _get_due_date(self, record):
    today = datetime.today()
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    # if due_date > today:
    return due_date - today

  def _get_overdue_value(self, record):
    flag = False
    today = datetime.today()
    overdue = None
    due_date = datetime.strptime(record.due_date, '%Y-%m-%d')
    if record.paid_flag:
      today = datetime.strptime(record.payment_date, '%Y-%m-%d')
    if due_date < today:
      flag=True
      overdue = today - due_date

    return flag,overdue

  def _update_date(self, customer=False):
    records = self.search([])
    overdue_invoices = []
    due_invoices_current = []
    due_invoices_next = []
    customer_data_navnidhi = {}
    customer_data_infratech = {}
    sale_person_data = {}
    company_navnidhi = None
    company_infratech = None

    for record in records:
      if record.payment_date: continue
      flag, overdue = self._get_overdue_value(record)
      due_resp = self._get_due_date(record)
      customer_emails = self._get_customer_email_list(record)

      if 'Navnidhi' in record.company.name and not record.customer.id in customer_data_navnidhi:
        company_navnidhi = record.company
        customer_data_navnidhi[record.customer.id] = {'mail_to': customer_emails[0],
                                             'mail_cc': customer_emails[1:len(customer_emails)],
                                             'overdue': [], 'due': []}

      if 'Infratech' in record.company.name and not record.customer.id in customer_data_infratech:
        company_infratech = record.company
        customer_data_infratech[record.customer.id] = {'mail_to': customer_emails[0],
                                             'mail_cc': customer_emails[1:len(customer_emails)],
                                             'overdue': [], 'due': []}


      if not record.sales_person.id in sale_person_data:
        sale_person_data[record.sales_person.id] = {'mail_to': record.sales_person.email, 'mail_cc':[],
                                                    'overdue': [], 'due': []}

      if overdue:
        if customer:
          record.write({'overdue': '%s Day(s)' % overdue.days, 'overdue_reminders': record.overdue_reminders + 1})
        if 'Infratech' in record.company.name:
          customer_data_infratech[record.customer.id]['overdue'].append(record)
        elif 'Navnidhi' in record.company.name:
          customer_data_navnidhi[record.customer.id]['overdue'].append(record)
        sale_person_data[record.sales_person.id]['overdue'].append(record)
        overdue_invoices.append(record)

      if due_resp and due_resp.days < 14 and due_resp.days > 0:
        if due_resp.days < 7:
          due_invoices_current.append(record)
        else:
          due_invoices_next.append(record)
        sale_person_data[record.sales_person.id]['due'].append(record)


    return {
      'customer_data_infratech': customer_data_infratech,
      'customer_data_navnidhi': customer_data_navnidhi,
      'company_infratech': company_infratech,
      'company_navnidhi': company_navnidhi,
      'sale_person_data': sale_person_data,
      'due_invoices_current': due_invoices_current,
      'due_invoices_next': due_invoices_next,
      'overdue_invoices': overdue_invoices
    }

  def _send_mail_company(self):
    data = self._update_date(customer=False)
    self._send_mail_to_record(data['sale_person_data'], 'guard_payments.sale_person_mail')
    context = {'due_invoices_current': data['due_invoices_current'],
               'due_invoices_next': data['due_invoices_next'],
               'overdue': data['overdue_invoices']}
    if len(data['due_invoices_current']) or len(data['due_invoices_next']) or len(data['overdue_invoices']):
      self.send_mail('guard_payments.admin_mail_invoices', self.get_mail_list(), context)
    return

  def _send_mail_customer(self):
    data = self._update_date(customer=True)
    self._send_mail_to_record(data['customer_data_infratech'], 'guard_payments.customer_mail', company_data=data['company_infratech'])
    self._send_mail_to_record(data['customer_data_navnidhi'], 'guard_payments.customer_mail', company_data=data['company_navnidhi'])
    return


  def _send_mail_to_record(self, record_list=[], mail_template=None, company_data = None):
    for record in record_list:
      if not len(record_list[record]['overdue']) and not len(record_list[record]['due']): continue
      context = {'overdue': record_list[record]['overdue'], 'due': record_list[record]['due']}
      if company_data:
        context.update({'company_data': company_data})
      template = self.env.ref(mail_template)
      template.email_to = record_list[record]['mail_to']
      template.email_cc = record_list[record]['mail_cc']
      template.with_context(context=context).send_mail(self.sudo().id)

  def _get_customer_email_list(self, record):
    email = []
    email.append(record.customer.email)
    if record.customer.email_second: email.append(record.customer.email_second)
    if record.customer.email_third: email.append(record.customer.email_third)
    if record.customer.email_fourth: email.append(record.customer.email_fourth)
    return  email

  def create_excel_sheet(self, data=None):
    if not data:
      return False

    field_names = ['invoice_number', 'invoice_date', 'customer', 'amount', 'payment_due', 'overdue','paid_flag','payment_date' ,'overdue_flag', 'due']
    field_display_data = ['invoice_number', 'invoice_date', 'customer', 'amount', 'payment_due', 'overdue','paid_flag','payment_date' ]
    field_display_names = ['Invoice Number', 'Invoice Date', 'Customer', 'Amount', 'Payment Terms', 'Overdue Days', 'Paid','Payment Date']
    filter_arr = ['|', ('due_date','<=',fields.Date.today()),('due_date', '>', data['from']), ('due_date', '<=', data['to'])]
    if data['company_id']:
      filter_arr.append(('customer','=',int(data['company_id'])))

    guard_data = self.search_read(filter_arr, field_names)

    file_name = self.env['guard.interface'].create_excel_report('/tmp/report.xlsx', field_display_data, field_display_names,
                                                                sorted(guard_data, key=lambda x: x['due']), model='guard.invoices')
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


class ResCompany(models.Model):
  _inherit = 'res.company'

  account_number = fields.Char(string='Account Number')
  gstin_number = fields.Char(string='GSTIN')
  bank_name = fields.Char(string='Bank Name')
  bank_address = fields.Text(string='Bank Address')
  bank_ifsc = fields.Char(string='IFSC Code')
