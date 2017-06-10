# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class inherit_res_partner(models.Model):
#     _name = 'inherit_res_partner.inherit_res_partner'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class inherit_res_partner(models.Model):
	_name = 'inherited_res_partner'
	_inherit = 'res.partner'

	name = fields.Char()