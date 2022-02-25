from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO
from odoo.exceptions import ValidationError
import base64, urllib
import certifi
import urllib3
from xlrd import open_workbook, XLRDError, xldate_as_tuple
from datetime import datetime
import os
import string


class import_user_name(models.TransientModel):
    _name = 'import.user'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Import Excel')
    file_name = fields.Char('File name', readonly=True)

    def button_print(self):
        sheet1 = False
        book = False
        try:
            if self.excel_file:
                path = os.path.dirname(os.path.realpath(__file__)) + 'test.xlsx'
                data_file_p = open(path, 'wb')
                data_file_p.write((base64.b64decode(self.excel_file)))
                data_file_p.close()
                book = open_workbook(path)
                sheet1 = book.sheet_by_index(0)
        except XLRDError as e:
            raise UserError(f"Error Occurred: {e}")
        users_obj = self.env['res.users']
        user_lst = list()
        try:
            if sheet1:
                for row in range(1, sheet1.nrows):
                    print(sheet1.row_values(row))
                    data_dict = {}
                    if sheet1.row_values(row)[0]:
                        data_dict['emp_code'] = (int(sheet1.row_values(row)[0]))
                    if sheet1.row_values(row)[1]:
                        data_dict['name'] = (str(sheet1.row_values(row)[1])).strip()
                        data_dict['firstname'] = (str(sheet1.row_values(row)[1]).partition(' ')[0])
                        data_dict['lastname'] = (str(sheet1.row_values(row)[1]).partition(' ')[2])
                    if sheet1.row_values(row)[2]:
                        data_dict['designation'] = (str(sheet1.row_values(row)[2])).strip()
                    if sheet1.row_values(row)[3]:
                        data_dict['band'] = (str(sheet1.row_values(row)[3])).strip()
                    if sheet1.row_values(row)[4]:
                        data_dict['gender'] = (str(sheet1.row_values(row)[4]).lower())
                    if sheet1.row_values(row)[5]:
                        data_dict['role_custom'] = (str(sheet1.row_values(row)[5]))
                    if sheet1.row_values(row)[6]:
                        data_dict['work_location'] = (str(sheet1.row_values(row)[6])).strip()
                    if sheet1.row_values(row)[7]:
                        data_dict['region'] = (str(sheet1.row_values(row)[7]).lower())
                    if sheet1.row_values(row)[9]:
                        state_val = (str(sheet1.row_values(row)[9]).title()).strip()
                        state_val_id = self.env['res.country.state'].search([('name', '=', state_val)], limit=1)
                        if not state_val_id:
                            raise UserError(_('State %s does not exist in odoo') % (state_val))
                        data_dict['state_id'] = state_val_id.id
                    if sheet1.row_values(row)[8]:
                        country_val = (str(sheet1.row_values(row)[8])).strip()
                        country_val_id = self.env['res.country'].search([('name', '=', country_val)], limit=1)
                        if not country_val_id:
                            raise UserError(_('Country %s does not exist in odoo') % (country_val))
                        data_dict['country_id'] = country_val_id.id

                    if sheet1.row_values(row)[10]:
                        data_dict['city'] = (str(sheet1.row_values(row)[10]))
                    if sheet1.row_values(row)[11]:
                        data_dict['phone_number1'] = int(sheet1.row_values(row)[11])
                    if sheet1.row_values(row)[12]:
                        data_dict['login'] = str(sheet1.row_values(row)[12])

                    data_dict['login_type'] = 'employee-onroll'
                    data_dict['is_employee'] = 'True'
                    user_lst.append(data_dict)
            users = users_obj.sudo().create(user_lst)
            print(users,"users")
            for user in users:
                customer_role_id = self.env['res.users.role'].sudo().search([('name', '=', 'Users')])
                # user_role_id = self.env.ref('ecom_lms.users_role')
                if not customer_role_id:
                    raise UserError("User role not found")
                vals = [(0, 0, {'role_id': customer_role_id.id})]
                # vals = [(0, 0, {'role_id': user_role_id.id})]
                user.update({'role_line_ids': vals})
                if user.partner_id:
                    if user.pincode:
                        user.partner_id.zip = user.pincode
                    if user.city:
                        user.partner_id.city = user.city
                    if user.phone_number1:
                        user.partner_id.phone = user.phone_number1
                    if user.street_address:
                        user.partner_id.street = user.street_address
                    if user.state_id:
                        user.partner_id.state_id = user.state_id.id
                    if user.country_id:
                        user.partner_id.country_id = user.country_id.id

            message_id = self.env['message.wizard'].create({'message': _("Employee details uploaded successfully")})
            return {
                'name': _('Successfull'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                # pass the id
                'res_id': message_id.id,
                'target': 'new'
            }


        except Exception as e:
            print("error", e)
            raise UserError(f"Error Occurred: {e}")

