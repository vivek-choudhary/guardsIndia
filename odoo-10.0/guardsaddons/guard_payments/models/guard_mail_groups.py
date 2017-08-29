# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GuardMail(models.Model):
  _name = 'guard.mail'
  _sql_constraints = [
        ('email',
         'UNIQUE (email)',
         'Email number must be unique!')]

  name=fields.Char(string='Email')
  group_id = fields.Many2one('guard.mail_group')

class GuardMailGroups(models.Model):
  _name = 'guard.mail_group'
  _description = 'Guard Mail Group'
  _sql_constraints = [
        ('name',
         'UNIQUE (name)',
         'Email number must be unique!')]


  name = fields.Char(string='Group Name', required=True)
  email_ids = fields.One2many('guard.mail', 'group_id')
