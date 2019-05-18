# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    tin_number = fields.Char(string='TIN Number')
    gst_number = fields.Char(string='GST Number')


class EmailRecords(models.Model):
    _name = 'email.records'

    name = fields.Char(string='Person Name')
    mail = fields.Char(string='Email ID')


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    mail_ids = fields.Many2many('email.records', relation='partner_email_record_rel',
                                column1='partner_id', column2='record_id')