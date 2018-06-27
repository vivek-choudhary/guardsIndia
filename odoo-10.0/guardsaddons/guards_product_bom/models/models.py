# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GuardsBomProducts(models.Model):
  _name = 'guards.product.bom'
  _description = 'Guards Product BOM'

  product_id = fields.Many2one(comodel_name='guards.product', string='Product', required=True)
  quantity = fields.Integer(string='Quantity', required=True)
  bom_id = fields.Many2one(comodel_name='guards.bom')
  product_uom_id = fields.Many2one('guards.stock.uom', string='Unit')


class GuardsBom(models.Model):
  _name = 'guards.bom'
  _description = 'Guards Product BOM'

  name = fields.Char(string='BOM Name')
  bom_product_ids = fields.One2many(comodel_name='guards.product.bom',inverse_name='bom_id',string='Product BOM')
  product_id = fields.Many2one(comodel_name='guards.product', string='Product', required=True)
  notes = fields.Text(string='Extra Notes')
  active = fields.Boolean(string='Active', default=True)

  def get_product_quantites_dict(self, bom, quantity):
    product_dir = bom.bom_product_ids.mapped(lambda x: (x.product_id, x.quantity * quantity))
    return product_dir

  @api.model
  def get_product_quantities_dict_widget(self, bom_id, quantity):
    if not bom_id or not quantity:
      raise Exception, 'Insuficient Paramenters'
    bom_obj = self.browse(int(bom_id))
    product_dir = self.get_product_quantites_dict(bom_obj, int(quantity))
    mapped_product_dir = map(lambda x: {'name': x[0].name, 'required_quantity':(x[1] - x[0].net_quantity),'product_quantity': x[0].net_quantity}, product_dir)
    return mapped_product_dir

class GuardsProductInherit(models.Model):
  _name = 'guards.product'
  _inherit = 'guards.product'

  bom_ids = fields.One2many(comodel_name='guards.bom', string='Product BOM', inverse_name='product_id')


