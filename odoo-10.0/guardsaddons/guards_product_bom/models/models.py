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

    name = fields.Char(string='BOM Name', required=True)
    bom_product_ids = fields.One2many(comodel_name='guards.product.bom',inverse_name='bom_id',string='Product BOM')
    product_id = fields.Many2one(comodel_name='guards.product', string='Product', required=True)
    notes = fields.Text(string='Extra Notes')
    active = fields.Boolean(string='Active', default=True)


class GuardsProductInherit(models.Model):
  _name = 'guards.product'
  _inherit = 'guards.product'

  bom_ids = fields.One2many(comodel_name='guards.bom', string='Product BOM', inverse_name='product_id')


