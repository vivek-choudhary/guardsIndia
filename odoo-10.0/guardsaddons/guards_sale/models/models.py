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
  product_type = fields.Char(string='Product Type', compute='_get_product_type', store=False)

  @api.depends('product_id')
  def _get_product_type(self):
    for product in self:
      product.product_type = product.product_id.type if product.product_id.type else ''

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
    seller_company = fields.Many2one(comodel_name='res.company', string='Seller Company', required=True)
    amount = fields.Float(compute='_get_total_amount', string='Amount', store=True)
    status = fields.Selection(selection=[('draft','Draft'),('confirm','Confirm')])
    invoice_number = fields.Char(string='Invoice Number')
    inventory_check_status = fields.Boolean(string='Inventory Status', compute='_update_inventory_status')
    bom_product_quantities = fields.Text(compute='_get_bom_product_quantities', string='BOM Product Quantites')
    comment = fields.Text(string='Comment')
    # bom_product_quantities = fields.Selection(selection=[(1,1)])
    # taxes = fields.One2many(comodel_name='guards.tax')

    @api.depends('sale_product_ids')
    def _get_total_amount(self):
      total_cost = 0
      for record in self:
        total_cost = sum(map(lambda x: x.user_sale_price, record.sale_product_ids),0)
      record.amount = total_cost

    @api.depends('sale_product_ids')
    # The function prepares the data in the format ["A:12","B:12"] as the BOM widget reads the data in the given format.
    def _get_bom_product_quantities(self):
      guards_bom_env = self.env['guards.bom']
      bom_quantities_per_product = []
      product_dict = {}

      for sale_product_id in self.sale_product_ids:
        if sale_product_id.product_bom_id:
          product_quantities = guards_bom_env.get_product_quantites_dict(sale_product_id.product_bom_id, sale_product_id.quantity, product_dir={})
          product_dict = self.update_product_dict(product_dict, product_quantities )
        else:
          product_dict = self.update_product_dict(product_dict,{sale_product_id.product_id.id: (sale_product_id.product_id, sale_product_id.quantity)})

      # Preparing the product dict format {product_id: required_quantity: inventory}
      bom_quantities_per_product.extend(map(lambda x: "%s:%s:%s"%(str(product_dict[x][0].name), (product_dict[x][1] - product_dict[x][0].net_quantity), product_dict[x][0].net_quantity), product_dict))
      self.bom_product_quantities = bom_quantities_per_product
      return

    def update_product_dict(self, existing_dict, product_tuple_dict):
      for product in product_tuple_dict:
        if existing_dict.has_key(product):
          new_hash = {product: (existing_dict[product][0], existing_dict[product][1] + product_tuple_dict[product][1])}
        else:
          new_hash = {product: (product_tuple_dict[product][0], product_tuple_dict[product][1])}
        existing_dict.update(new_hash)
      return existing_dict

    @api.depends('sale_product_ids')
    def _update_inventory_status(self):
      # To be used with single length self object
      status_flags = []
      guards_stock_env = self.env['guards.stock']
      guards_bom_env = self.env['guards.bom']

      for sale_product_id in self.sale_product_ids:
        if sale_product_id.product_bom_id:
          product_quantities = guards_bom_env.get_product_quantites_dict(sale_product_id.product_bom_id, sale_product_id.quantity, product_dir={})
          status_flags.extend(map(lambda x: guards_stock_env.check_product_inventory(product_quantities[x][0], product_quantities[x][1]), product_quantities))
        else:
          status_flags.extend([guards_stock_env.check_product_inventory(sale_product_id.product_id, sale_product_id.quantity)])
      self.inventory_check_status = all(status_flags)

    # To be used with single self object
    def confirm_sale(self):
      # TODO: Move creation for a sale object with no BOM
      # Used for creation of 'OUT' moves as according to the products in the BOM
      for sale_product_id in self.sale_product_ids:
        # if not sale_product_id.product_bom_id and not sale_product_id.quantity:
        #   raise UserError(_('%s: At least one should be present. Either BOM or UOM.')%(sale_product_id.product_id.name))

        self._recursive_product_creation(sale_product_id)
        self.status = 'confirm'
      return True

    # Creation of multilevel stock moves
    def _recursive_product_creation(self, sale_product_id):
      if sale_product_id.product_type == 'bom':
        products = self.env['guards.bom'].get_product_quantites_dict(sale_product_id.product_bom_id, sale_product_id.quantity, product_dir={})
      elif sale_product_id.product_type == 'raw':
        products = {sale_product_id.product_id.id: (sale_product_id.product_id, sale_product_id.quantity)}
      for product in products:
        self._create_stock_move(products[product][0].id, None, products[product][1])
      return

    def _create_stock_move(self, product_id, product_uom_id, quantity):
      try:
        move_values = {
          'product_id': product_id,
          'product_uom': product_uom_id,
          'quantity': quantity
        }
        self.env['guards.product.inventory.wizard'].create_out_move(move_values)
      except Exception as e:
        print e.message

      return True

    def get_sale_product_lines(self):
      pass

    def parse_string(self):
      result = []
      for ele in self.bom_product_quantities[1:len(self.bom_product_quantities)-1].split(','):
        result.append(ele.split(':'))
      return result
      pass