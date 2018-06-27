# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GuardsSaleProduct(models.Model):
  _name = 'guards.sale.product'
  _description = 'Selling Product with BOM'

  product_id = fields.Many2one(comodel_name='guards.product', string='Product')
  product_uom_id = fields.Many2one(comodel_name='guards.stock.uom', string='Product UOM')
  sale_id = fields.Many2one(comodel_name='guards.sale', string='Sale ID')
  product_bom_id = fields.Many2one(comodel_name='guards.bom', string='BOM')
  quantity = fields.Integer(string='Product Quantity')
  unit_sale_price = fields.Float(string='Unit Sale Price')
  bom_sale_price = fields.Float(string='System Sale Price', compute='_compute_bom_sale_price')
  user_sale_price = fields.Float(string='User Sale Price', compute='_compute_user_sale_price')

  @api.depends('product_bom_id', 'product_id', 'quantity')
  def _compute_bom_sale_price(self):
    for record in self:
      record_sale_price = 0
      for product in record.product_bom_id.bom_product_ids:
        product_quantity = product.quantity * record.quantity
        record_sale_price += product_quantity * product.product_id.sale_price
      record.total_sale_price = record_sale_price

  @api.depends('quantity', 'unit_sale_price')
  def _compute_user_sale_price(self):
    for record in self:
      record.user_sale_price = record.unit_sale_price * record.quantity



class GuardsSale(models.Model):
    _name = 'guards.sale'
    _description = 'Guards Sale Module'
    _rec_name = 'invoice_number'

    customer_partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', required=True)
    sale_product_ids = fields.One2many(comodel_name='guards.sale.product', inverse_name='sale_id',string='Products')
    sale_date = fields.Date(string='Sale Date', required=True)
    seller_company = fields.Many2one(comodel_name='res.partner', string='Seller Company', required=True)
    amount = fields.Float(compute='_get_total_amount', string='Amount', store=True)
    status = fields.Selection(selection=[('draft','Draft'),('confirm','Confirm')])
    invoice_number = fields.Char(string='Invoice Number')
    inventory_check_status = fields.Boolean(string='Inventory Status', compute='_update_inventory_status')
    # taxes = fields.One2many(comodel_name='guards.tax')

    @api.depends('sale_product_ids')
    def _get_total_amount(self):
      total_cost = 0
      for record in self:
        total_cost = sum(map(lambda x: x.user_sale_price, record.sale_product_ids),0)
      record.amount = total_cost

    @api.depends('sale_product_ids')
    def _update_inventory_status(self):
      # To be used with single length self object
      status_flags = []
      guards_stock_env = self.env['guards.stock']
      guards_bom_env = self.env['guards.bom']

      for sale_product_id in self.sale_product_ids:
        if sale_product_id.product_bom_id:
          product_quantities = guards_bom_env.get_product_quantites_dict(sale_product_id.product_bom_id, sale_product_id.quantity)
          status_flags.extend(map(lambda x: guards_stock_env.check_product_inventory(x[0], x[1]), product_quantities))
        else:
          status_flags.extend([guards_stock_env.check_product_inventory(sale_product_id.product_id, sale_product_id.quantity)])
      self.inventory_check_status = all(status_flags)

    # To be used with single self object
    def confirm_sale(self):
      for sale_product_id in self.sale_product_ids:
        if not sale_product_id.product_bom_id and not sale_product_id.product_uom_id:
          raise UserError(_('%s: At least one should be present. Either BOM or UOM.')%(sale_product_id.product_id.name))
        if not sale_product_id.product_bom_id:
          self.create_stock_move(sale_product_id.product_id, sale_product_id.product_bom_id, sale_product_id.quantity)
        else:
          for product in sale_product_id.product_bom_id.bom_product_ids:
            self.create_stock_move(product.product_id, product.product_uom_id , sale_product_id.quantity * product.quantity)
        self.status = 'confirm'
      return True

    def create_stock_move(self, product, product_uom, quantity):
      try:
        move_values = {
          'product_id': product.id,
          'product_uom': product_uom.id,
          'quantity': quantity
        }
        self.env['guards.product.inventory.wizard'].create_out_move(move_values)
      except Exception as e:
        print e.message

      return True