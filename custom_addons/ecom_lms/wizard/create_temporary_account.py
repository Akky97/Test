# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import string
import random
import re
from datetime import timedelta
from xlrd import open_workbook, XLRDError, xldate_as_tuple
from datetime import datetime
import base64, urllib
import certifi
import urllib3
import os


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


class TemporaryAccount(models.TransientModel):
    _name = "temporary.account"

    upload_file = fields.Binary(string="Upload File")
    file_name = fields.Char(string="Filename")

    # def generate_account(self):
    #
    #     user_dict = dict()
    #     if not (re.fullmatch(regex, self.email_id)):
    #         raise UserError(f"Email is invalid, please check the email.")
    #     pre_joinee_role = self.env['res.users.role'].search([('name', '=', 'Pre Joinee Role')],limit=1)
    #     role_vals = {
    #         'role_id': pre_joinee_role.id,
    #         'date_from': fields.Date.to_date(fields.Date.today()),
    #         'date_to': fields.Date.to_date(fields.Date.today() + timedelta(days=30)),
    #     }
    #     user_group_id = self.env.ref('base.group_user').id
    #     user_dict.update({
    #         'name': self.user_name,
    #         'login': self.email_id,
    #         'groups_id': [(6, 0, [user_group_id])],
    #         'role_line_ids': [(0, 0, role_vals)]
    #     })
    #     try:
    #         users = self.env['res.users'].sudo().create(user_dict)
    #         if users.exists():
    #             print(f"Account Created{users}")
    #     except Exception as e:
    #         print(f"Exception in create temporary account: {e}")
    #         raise UserError(f"Error Occurred:{e}")

    def generate_account(self):
        sheet1 = False
        book = False
        try:
            if self.upload_file:
                path = os.path.dirname(os.path.realpath(__file__)) + 'test.xlsx'
                data_file_p = open(path, 'wb')
                data_file_p.write((base64.b64decode(self.upload_file)))
                data_file_p.close()
                book = open_workbook(path)
                sheet1 = book.sheet_by_index(0)
        except XLRDError as e:
            raise UserError(f"Error Occurred: {e}")
        users_obj = self.env['res.users']
        user_lst = list()
        try:
            if sheet1:
                for row in range(1,sheet1.nrows):
                    print(sheet1.row_values(row))
                    data_dict = {}
                    if sheet1.row_values(row)[0]:
                        data_dict['firstname'] = (str(sheet1.row_values(row)[0])).strip()
                    if sheet1.row_values(row)[1]:
                        data_dict['middlename'] = (str(sheet1.row_values(row)[1])).strip()
                    if sheet1.row_values(row)[2]:
                        data_dict['lastname'] = (str(sheet1.row_values(row)[2])).strip()
                    if sheet1.row_values(row)[0]:
                        if str(sheet1.row_values(row)[1]):
                            data_dict['name'] = (str(sheet1.row_values(row)[0])).strip() + ' ' + \
                                                (str(sheet1.row_values(row)[1])).strip() + ' '+ \
                                                (str(sheet1.row_values(row)[2])).strip()
                        else:
                            data_dict['name'] = (str(sheet1.row_values(row)[0])).strip() + ' ' + \
                                                (str(sheet1.row_values(row)[2])).strip()

                    if sheet1.row_values(row)[12]:
                        data_dict['login'] = (str(sheet1.row_values(row)[12])).strip()
                    if sheet1.row_values(row)[3]:
                        data_dict['phone_number1'] = (int(sheet1.row_values(row)[3]))
                    if sheet1.row_values(row)[4]:
                        data_dict['phone_number2'] = (int(sheet1.row_values(row)[4]))
                    if sheet1.row_values(row)[5]:
                        data_dict['street_address'] = (str(sheet1.row_values(row)[5])).strip()
                    if sheet1.row_values(row)[6]:
                        data_dict['city'] = (str(sheet1.row_values(row)[6])).strip()
                    if sheet1.row_values(row)[7]:
                        state_val=(str(sheet1.row_values(row)[7])).strip()
                        state_val_id= self.env['res.country.state'].search([('name','=',state_val)],limit=1)
                        if not state_val_id:
                            raise UserError(_('State %s does not exist in odoo')% (state_val))
                        data_dict['state_id'] = state_val_id.id
                    if sheet1.row_values(row)[8]:
                        country_val=(str(sheet1.row_values(row)[8])).strip()
                        country_val_id= self.env['res.country'].search([('name','=',country_val)],limit=1)
                        if not country_val_id:
                            raise UserError(_('Country %s does not exist in odoo')% (country_val))
                        data_dict['country_id'] = country_val_id.id
                    if sheet1.row_values(row)[9]:
                        data_dict['pincode'] = (int(sheet1.row_values(row)[9]))
                    if sheet1.row_values(row)[10]:
                        a1 = sheet1.row_values(row)[10]
                        dob_date = datetime(*xldate_as_tuple(a1, book.datemode))
                        data_dict['date_of_birth'] = dob_date.date()

                    if sheet1.row_values(row)[11]:
                        data_dict['gender'] = str(sheet1.row_values(row)[11]).strip()
                    if sheet1.row_values(row)[12]:
                        data_dict['email'] = str(sheet1.row_values(row)[12]).strip()
                        
                    if sheet1.row_values(row)[13]:
                        data_dict['region'] = (str(sheet1.row_values(row)[13])).strip()
                        
                    # data=''    
                    # if sheet1.row_values(row)[14]:
                    #     http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                    #                        ca_certs=certifi.where())
                    #
                    #     if "http://" in sheet1.row_values(row)[14] or "https://" in sheet1.row_values(row)[14]:
                    #         link = sheet1.row_values(row)[14]
                    #         image_response = http.request('GET', link)
                    #         image_thumbnail = base64.b64encode(image_response.data)
                    #         data=image_thumbnail
                    #
                    #     if "/home" in sheet1.row_values(row)[14]:
                    #         with open(sheet1.row_values(row)[14], 'rb') as file:
                    #             data = base64.b64encode(file.read())
                    #
                    # if not data:
                    #     raise UserError("Image is required for all users")
                    # data_dict['image_1920']=data    

                    data_dict['login_type'] = 'candidate'
                    pre_code = ''.join(random.choices(string.ascii_uppercase +
                                                  string.digits, k=8))
                    data_dict['pre_joinee_code']= pre_code
                    user_lst.append(data_dict)
            users = users_obj.sudo().create(user_lst)

            for user in users:
                user_role_id = self.env.ref('ecom_lms.users_role')
                # pre_joinee_role_id = self.env['res.users.role'].sudo().search([('name', '=', 'Pre Joinee Role')])
                if not user_role_id:
                    raise UserError("User role not found")
                vals = [(0, 0, {'role_id': user_role_id.id})]
                # vals = [(0, 0, {'role_id': pre_joinee_role_id.id,'is_prejoinee':True})]
                user.update({'role_line_ids': vals,'is_prejoinee':True})
                if user.partner_id:
                    if user.pincode:
                        user.partner_id.zip=user.pincode
                    if user.city:
                        user.partner_id.city=user.city
                    if user.phone_number1:
                        user.partner_id.phone=user.phone_number1
                    if user.street_address:
                        user.partner_id.street=user.street_address
                    if user.state_id:
                        user.partner_id.state_id=user.state_id.id
                    if user.country_id:
                        user.partner_id.country_id=user.country_id.id
                        
            message_id = self.env['message.wizard'].create({'message': _("Prejoinee details uploaded successfully")})
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
            print("error",e)
            raise UserError(f"Error Occurred: {e}")

