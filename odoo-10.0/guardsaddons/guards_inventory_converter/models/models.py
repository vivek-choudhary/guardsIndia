# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GuardsStockConversions(models.Model):
  _name = 'guards.stock.conversion'
  _description = '''Used for the conversion of stock from one UOM to another. Applicable for only BOM type products'''

  name = fields.Char(string='')
  product_id = fields.Many2one(comodel_name='guards.product', string='Guards Product', required=True)
  from_uom_id = fields.Many2one(comodel_name='guards.stock.uom', string='From UOM', required=True)
  to_uom_id = fields.Many2one(comodel_name='guards.stock.uom', string='To UOM', required=True)
  conversion_ratio = fields.Float(string='Conversion Ratio', default = 0.0, required=True)

  def get_converted_quantity(self, quantity):
    converted_value = 0.0
    return converted_value


class GuardsProductInheritConverter(models.Model):
  _name = 'guards.product'
  _inherit = 'guards.product'
  _description = 'Guards Product Inherit Stock'

  base_uom = fields.Many2one(comodel_name='guards.stock.uom')
  conversion_ids = fields.One2many(comodel_name='guards.stock.conversion', inverse_name='product_id')

  def get_converted_quantity(self, input_qunatity, product_uom):
    quantity = 0.0

    if self.type == 'raw':
      quantity = input_qunatity
    else:
      try:
        ratio = self._get_conversion_ratio(product_uom)
        quantity = product_uom*input_qunatity
      except Exception as e:
        ValueError(e.message)

    return quantity

  def _get_conversion_ratio(self, to_uom):
    conversion_objs = self.conversion_ids
    for obj in conversion_objs:
      if to_uom.name == obj.to_uom_id.name:
        return obj.convesion_ratio
    raise 'No conversion ratio found'


class GuardsSaleProductInheritConverter(models.Model):
  _name = 'guards.sale.product'
  _inherit = 'guards.sale.product'
  _description = 'Guards sale inherit for conversions'

  input_quantity = fields.Float(string='Input Quantity')

  @api.onchange('input_quantity')
  def update_quantity(self):
    if self.input_quantity == 0.0:
      return
    if not self.product_id.base_uom:
      raise UserError(_('No base unit defined for the product %s',self.product_id.name))
      return
    if self.product_id.base_uom.id == self.product_uom.id:
      self.quantity = self.input_quantity
      return
    self.quantity = self.product_id.get_converted_quantity(self.input_quantity, self.product_uom)

class GuardsPurchaseInheritConverter(models.Model):
  _name = 'guards.purchase.line'
  _inherit = 'guards.purchase.line'
  _description = 'Guards sale inherit for conversions'

  input_quantity = fields.Float(string='Input Quantity')

  @api.onchange('input_quantity')
  def update_quantity(self):
    if self.product_id.base_uom.id == self.product_uom.id:
      self.quantity = self.input_quantity
      return
    self.quantity = self.product_id.get_converted_quantity(self.input_quantity, self.product_uom)