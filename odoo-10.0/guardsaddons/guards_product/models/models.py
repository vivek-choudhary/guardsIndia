# -*- coding: utf-8 -*-

from odoo import models, fields, api
from functools import reduce

class guardsProducts(models.Model):
  _name = 'guards.product'
  _description = 'Guard Product'

  name = fields.Char(string='Product Name', store=True, reqired=True)
  description = fields.Text(string='Product Description')
  internal_reference = fields.Char(string='Internal Reference')
  sale_price = fields.Float(string='Sale Price')
  cost_price = fields.Float(string='Cost Price')
  active = fields.Boolean(string='Active', default=True)

  _sql_constraints = [
    ('guards_product_uniqueness',
     'UNIQUE (name)',
     'Name of the product must be unique'
     )
  ]
