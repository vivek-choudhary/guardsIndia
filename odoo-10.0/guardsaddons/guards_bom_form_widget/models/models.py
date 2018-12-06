# -*- coding: utf-8 -*-

from odoo import models, fields, api

class guardsBomFormWidget(models.TransientModel):
  _name = 'bom.form.widget'

  def create_excel_file(self, bom_id, quantity, file_name):
    product_dict = self.env['guards.bom'].get_product_quantities_dict_widget(bom_id, quantity)
    field_names = ['Product Name', 'Inventory', 'Required Quantity']
    self.create_excel(field_names, product_dict, file_name)
    return True


  def create_excel(self, field_names, product_dict, file_name):
    try:
      import xlsxwriter

      workbook = xlsxwriter.Workbook(file_name)
      bold = workbook.add_format({'bold': True})
      worksheet = workbook.add_worksheet()

      # Creating Heading Columns
      worksheet.write_row('A1', field_names, bold)

      row = 1
      for data in product_dict:
        row_data = [data['name'], data['product_quantity'], data['required_quantity']]
        worksheet.write_row(row, 0, row_data)
        row += 1

      workbook.close()
      return file_name
    except Exception as e:
      raise RuntimeError, 'Unable to create Sheet. '+e.message
    return True