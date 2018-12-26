# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class GuardsBomProducts(models.Model):
  _name = 'guards.product.bom'
  _description = 'Guards Product BOM'

  product_id = fields.Many2one(comodel_name='guards.product', string='Product', required=True)
  quantity = fields.Float(string='Quantity', required=True, digits=(0,4))
  bom_id = fields.Many2one(comodel_name='guards.bom')
  product_uom_id = fields.Many2one('guards.stock.uom', string='Unit')


class GuardsBom(models.Model):
  _name = 'guards.bom'
  _description = 'Guards Product BOM'

  name = fields.Char(string='BOM Name')
  bom_product_ids = fields.One2many(comodel_name='guards.product.bom', inverse_name='bom_id', string='Product BOM')
  product_id = fields.Many2one(comodel_name='guards.product', string='Product', required=True)
  notes = fields.Text(string='Extra Notes')
  active = fields.Boolean(string='Active', default=True)

  @api.onchange('product_id')
  def check_bom(self):
    if self._check_existing_product_bom(self.product_id):
      raise exceptions.except_orm(_('Product BOM Exists'), _('The BOM for the corresponding product already exists'))

  def _check_existing_product_bom(self, product_id):
    existing_bom = self.search([('product_id','=',self.product_id.id)])
    return existing_bom if len(existing_bom) else False

  @api.model
  def create(self, vals):
    existing_products = self._check_existing_product_bom(vals['product_id'])
    if existing_products:
      self._deactivate_existing_products(existing_products)
    return super(GuardsBom, self).create(vals)

  def _deactivate_existing_products(self, product_ids):
    return True

  def get_product_quantites_dict(self, bom, quantity, product_dir):
    # Returns a hash of the product ids corresponding to their quantity.

    for bom_product in bom.bom_product_ids:
      if len(bom_product.product_id.bom_ids):
        product_dir = self.get_product_quantites_dict(bom_product.product_id.bom_ids[-1], quantity * bom_product.quantity, product_dir)
      else:
        product_dir = self._add_product_to_dict(product_dir, bom_product, quantity * bom_product.quantity)
    return product_dir

  def _add_product_to_dict(self, product_dir, bom_product, quantity):
    if bom_product.product_id.id in product_dir:
      product_dir[bom_product.product_id.id] = (bom_product.product_id, product_dir[bom_product.product_id.id][1] + quantity)
    else:
      product_dir.update({bom_product.product_id.id: (bom_product.product_id, quantity)})
    return product_dir

  @api.model
  def get_product_quantities_dict_widget(self, bom_id, quantity):
    if not bom_id or not quantity:
      raise Exception, 'Insufficient Parameters'
    bom_obj = self.browse(int(bom_id))
    product_dir = self.get_product_quantites_dict(bom_obj, int(quantity), product_dir={})
    mapped_product_dir = map(lambda x: {'name': product_dir[x][0].name, 'required_quantity':(product_dir[x][1] - product_dir[x][0].net_quantity),
                                        'product_quantity': product_dir[x][0].net_quantity}, product_dir)
    return mapped_product_dir

class GuardsProductInherit(models.Model):
  _name = 'guards.product'
  _inherit = 'guards.product'

  bom_ids = fields.One2many(comodel_name='guards.bom', string='Product BOM', inverse_name='product_id')


