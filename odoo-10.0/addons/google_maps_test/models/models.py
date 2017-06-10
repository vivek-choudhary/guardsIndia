# -*- coding: utf-8 -*-

from odoo import models, fields, api

class google_maps_test(models.Model):
    _name = 'google_maps_test.google_maps_test'

    locationName = fields.Char(name="Location Name")
    value = fields.Text(name = "Value")