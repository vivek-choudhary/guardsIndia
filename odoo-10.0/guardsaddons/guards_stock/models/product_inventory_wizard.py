from odoo import api, models,fields
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class productInventoryWizard(models.TransientModel):
  _name = 'guards.product.inventory.wizard'

  product_id = fields.Many2one('guards.product', string='Product')
  quantity = fields.Integer(string='Quantity')
  product_uom = fields.Many2one('guards.stock.uom', string='Unit')

  def create_stock(self, values):
    stock_values = {
      'product_id': values['product_id'],
      'product_uom': values['product_uom']
    }
    return self.env['guards.stock'].create(stock_values)

  def create_move(self, values):
    stock = self.env['guards.stock'].search([('product_id','=',values['product_id'])])
    if not len(stock):
      stock = self.create_stock(values)

    move_values = {
      'stock_id': stock.id,
      'product_id': values['product_id'],
      'quantity': values['quantity'],
      'type': 'in',
      'product_uom': values['product_uom']
    }
    res = self.env['guards.stock.move'].create(move_values)
    return res

  def create_out_move(self, values):
    stock = self.env['guards.stock'].search([('product_id','=',values['product_id'])])
    if not len(stock):
      stock = self.create_stock(values)

    move_values = {
      'stock_id': stock.id,
      'product_id': values['product_id'],
      'quantity': values['quantity'],
      'type': 'out',
      'product_uom': values['product_uom']
    }
    res = self.env['guards.stock.move'].create(move_values)
    return res

  def update_inventory(self):
    if self.quantity == 0:
      raise UserError('Inventory Cannot Be 0')
    values = {
      'product_id': self.product_id.id,
      'quantity': self.quantity,
      'product_uom': self.product_uom.id,

    }
    self.create_move(values)
    return
