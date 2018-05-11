# -*- coding: utf-8 -*-

from odoo import models, fields, api

class guardsStockUom(models.Model):
  _name = 'guards.stock.uom'
  _description = 'Guards Stock UOM'

  name = fields.Char(string='Unit Name')
  abbrevation = fields.Char(string='Abbreviation')

class stockMoves(models.Model):
  _name = 'guards.stock.move'
  _description = 'Guards Stock Move'

  type = fields.Selection(selection=[('in','In'), ('out','Out')], string='Move Type')
  quantity = fields.Integer(string='Move Quantity', default=0)
  stock_id = fields.Many2one(comodel_name='guards.stock', string='Stock Reference' )
  product_id = fields.Many2one(comodel_name='guards.product', string='Product')
  product_uom = fields.Many2one(comodel_name='guards.stock.uom', string='Unit')


class guardsStock(models.Model):
  _name = 'guards.stock'
  _description = 'Guard Stock'

  product_id = fields.Many2one(comodel_name='guards.product', string='Product', delegate=True)
  product_qty = fields.Integer(string='Product Quantity', compute='_get_moves_quantity')
  product_uom = fields.Many2one(comodel_name='guards.stock.uom', string='Unit')
  move_ids = fields.One2many(comodel_name='guards.stock.move', inverse_name='stock_id')

  @api.depends('move_ids')
  def _get_moves_quantity(self):
    for ele in self:
      type_in = ele.move_ids.filtered(lambda r: r.type== "in").mapped('quantity')
      type_out = ele.move_ids.filtered(lambda r: r.type== "out").mapped('quantity')
      if not len(type_in):
        return 0
      ele.product_qty = reduce((lambda x,y: x + y), type_in, 0) - reduce((lambda x,y: x + y), type_out, 0)
  
  @api.model
  def create(self, values):
    return super(guardsStock, self).create(values)
  
  @api.model
  def write(self, values):
    return super(guardsStock, self).write(values)



class guardsProductIntheritStock(models.Model):
  _name = 'guards.product'
  _inherit = 'guards.product'
  _description = 'Guards Product Inherit Stock'

  stock_ids = fields.One2many(comodel_name='guards.stock', string='Stocks', inverse_name='product_id')
  net_quantity = fields.Integer(compute="_inventory_value", store=False)

  @api.depends('stock_ids')
  def _inventory_value(self):
    for ele in self:
      mapped_ids = ele.stock_ids.mapped('product_qty')
      if not len(mapped_ids):
        return 0
      ele.net_quantity = reduce((lambda x,y: x + y), mapped_ids)
    return

  def open_inventory_wizard(self):
    return {
      'type': 'ir.actions.act_window',
      'name': 'Update Product Inventory',
      'res_model': 'guards.product.inventory.wizard',
      'view_type': 'form',
      'view_mode': 'form',
      'context': {'default_product_id': self.id},
      'view_id': self.env.ref('guards_stock.product_update_inventory_view',False).id,
      'target': 'new',
    }
