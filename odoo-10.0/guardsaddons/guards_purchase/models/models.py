# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class guardsPurchaseLines(models.Model):
  _name = 'guards.purchase.line'

  product_id = fields.Many2one('guards.product', string='Product', required=True)
  quantity = fields.Float('Quantity', required=True)
  product_uom = fields.Many2one('guards.stock.uom', string='Product Unit')
  purchase_id = fields.Many2one('guards.purchase', string='Purchase')
  cost = fields.Float(string='Cost', default=0.0)
  total_cost = fields.Float(string='Total Cost', store=False, compute='_get_total_cost')
  product_bom = fields.Many2one(comodel_name='guards.bom', string='Product BOM')
  product_type = fields.Char(string='Product Type', compute='_get_product_type', store=False)

  @api.depends('product_id')
  def _get_product_type(self):
    for product in self:
      product.product_type = product.product_id.type if product.product_id.type else ''

  @api.depends('cost', 'quantity')
  def _get_total_cost(self):
    for ele in self:
      ele.total_cost = ele.cost * ele.quantity
    return

  @api.onchange('product_id')
  def update_cost(self):
    if not self.product_id == None:
      self.cost = self.product_id.cost_price

  @api.model
  def create(self, values):
    if values['quantity'] == 0:
      raise UserError('Quantity Cannot Be Zero')
    return super(guardsPurchaseLines, self).create(values)


class guardsPurchase(models.Model):
  _name = 'guards.purchase'
  _description = 'Guards Purchase'
  _rec_name = 'invoice_number'

  partner_id = fields.Many2one('res.partner', string='Seller', required=True)
  invoice_number = fields.Char(string='Invoice')
  purchase_lines = fields.One2many(comodel_name='guards.purchase.line', inverse_name='purchase_id')
  status = fields.Selection(selection=[('draft', 'Draft'), ('confirm','Confirm')])
  total_cost = fields.Integer(compute='_get_total_cost')
  casting_weight = fields.Integer(string='Weight')
  purchase_date = fields.Date(string='Purchase Date', required=True)
  remark = fields.Text(string='Remark')

  @api.multi
  def unlink(self):
    from odoo import exceptions
    for ele in self:
      if ele.status == 'confirm':
        raise exceptions.UserError("Cannot Delete Confirmed Purchase")

  def _get_total_cost(self):
    for ele in self:
      mapped_values = ele.purchase_lines.mapped('total_cost')
      if len(mapped_values) == 0:
        ele.total_cost=0
      ele.total_cost = reduce((lambda x,y: x + y), mapped_values)
    return True

  def update_status(self):
    # Creation of 'IN' move lines as according the BOM provided.
    for element in self.purchase_lines:
      if element.product_bom.id:
        products = self.env['guards.bom'].get_product_quantites_dict(element.product_bom, element.quantity, product_dir={})
        for product in products:
          values = {
            'product_id': products[product][0].id,
            'product_uom': None,
            'quantity': products[product][1]
          }
          element.env['guards.product.inventory.wizard'].create_move(values)
      else:
        values ={
          'product_id': element.product_id.id,
          'product_uom': None,
          'quantity': element.quantity
        }
        element.env['guards.product.inventory.wizard'].create_move(values)

    self.status = 'confirm'
    return

  _sql_constraints = [
    ('guards_invoice_uniqueness',
     'UNIQUE (invoice_number, partner_id)',
     'Invoice Number corresponding to a partner must be unique'
     )
  ]
