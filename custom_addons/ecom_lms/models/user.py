from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

import io
import random
import string
import xlwt
from io import BytesIO
import base64
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO
import json
import requests
from collections import defaultdict


class ResUsers(models.Model):
    _inherit = 'res.users'
    _order = "id desc"

    firstname = fields.Char('First Name')
    device_token= fields.Char('Registration Key')
    middlename = fields.Char('Middle Name')
    lastname = fields.Char('Last Name')

    phone_number1 = fields.Char('Phone Number 1')
    phone_number2 = fields.Char('Phone Number 2')
    street_address = fields.Char('Street Address')

    city = fields.Char('City')
    pincode = fields.Char('Pincode')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    country = fields.Char('Country')
    date_of_birth = fields.Date('Date of birth')
    channel = fields.Char('Channel')
    region_from_website = fields.Char('Region')
    login_type = fields.Selection([
        ('employee-onroll', 'Employee On Roll'),
        ('employee-offroll', 'Employee Off Roll'),
        ('customer', 'Customer'),
        ('candidate', 'Candidate'),
    ], default='customer', string='Login Type')

    customer_code = fields.Char('Customer Code')
    is_customer = fields.Boolean('Customer', default=False)
    is_prejoinee = fields.Boolean('Pre Joinee', default=False)
    pre_joinee_code = fields.Char('Pre Joinee Code')
    is_employee = fields.Boolean('Employee', default=False)
    employee_code = fields.Char('Employee Code', compute="get_is_employee")
    designation = fields.Char('Designation')
    band = fields.Char('Band')
    role_custom = fields.Char('Role')
    work_location = fields.Char('Work Location')

    emp_code = fields.Char('Employee Code')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')

    ])
    home_region_from_website = fields.Char('Home Region')
    # regional_lead= fields.Boolean('Regional Lead', default=False)

    region = fields.Selection([('north', 'North'),
                               ('south', 'South'),
                               ('east', 'East'),
                               ('west', 'West'),
                               ('central', 'Central'),
                               ('ihq', 'IHQ')], string='Region')

    # topic_of_interest_ids =fields.Many2many('course.category','Topic Of Interest')
    topic_of_interest_ids = fields.Many2many('course.category', 'user_course_category_rel', 'user_id',
                                             'course_categ_id', string='Topic Of Interest')
    categ_from_website = fields.Char('Categ')
    lang_from_website = fields.Char('Lang')
    filter_lang_from_website = fields.Char('Filtered Language')
    my_journey_ids = fields.Many2many('course.journey', string='Journey', compute="_compute_journey_names")
    first_logged_in = fields.Boolean('1st Logged In',default=False)
    image_1920 = fields.Image(related='partner_id.image_1920', inherited=True, readonly=False, default=None)
    user_pw= fields.Char('User P/W')
    user_token= fields.Char('Token')
    
    
    def _set_password(self):
        ctx = self._crypt_context()
        hash_password = ctx.hash if hasattr(ctx, 'hash') else ctx.encrypt
        for user in self:
            user.user_pw=user.password
            self._set_encrypted_password(user.id, hash_password(user.password))

    @api.model
    def signup(self, values, token=None):
        """ signup a user, to either:
            - create a new user (no token), or
            - create a user for a partner (with token, but no user for partner), or
            - change the password of a user (with token, and existing user).
            :param values: a dictionary with field values that are written on user
            :param token: signup token (optional)
            :return: (dbname, login, password) for the signed up user
        """
        if token:
            # signup with a token: find the corresponding partner id
            partner = self.env['res.partner']._signup_retrieve_partner(token, check_validity=True, raise_exception=True)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})

            partner_user = partner.user_ids and partner.user_ids[0] or False

            # avoid overwriting existing (presumably correct) values with geolocation data
            if partner.country_id or partner.zip or partner.city:
                values.pop('city', None)
                values.pop('country_id', None)
            if partner.lang:
                values.pop('lang', None)

            if partner_user:
                code=''
                if partner_user.pre_joinee_code:
                    code= partner_user.pre_joinee_code
        
                elif partner_user.emp_code:
                    code= partner_user.emp_code
                elif partner_user.customer_code:
                    code= partner_user.customer_code
                else:
                    code=partner_user.login
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                partner_user.write(values)
                
                if not partner_user.login_date:
                    partner_user._notify_inviter()
                    
                return (self.env.cr.dbname, code, values.get('password'))
            else:
                # user does not exist: sign up invited user
                values.update({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'email': values.get('email') or values.get('login'),
                })
                if partner.company_id:
                    values['company_id'] = partner.company_id.id
                    values['company_ids'] = [(6, 0, [partner.company_id.id])]
                partner_user = self._signup_create_user(values)
                partner_user._notify_inviter()
        else:
            # no token, sign up an external user
            values['email'] = values.get('email') or values.get('login')
            self._signup_create_user(values)

        return (self.env.cr.dbname, values.get('login'), values.get('password'))
    
    
    @api.model
    def _get_login_domain(self, login):
        return ['|', '|', ('emp_code', '=', login), ('customer_code', '=', login), ('pre_joinee_code', '=', login)]

        return ['|','|',('emp_code', '=', login),('customer_code', '=', login),('pre_joinee_code', '=', login)]
    
    
    
    
    @api.onchange('region')
    def onchange_region(self):
        result = {}
        lst = []
        state_ids = False
        if self.region and not self.country_id:
            state_ids = self.env['res.country.state'].search([('region', '=', self.region)])
        if self.region and self.country_id:
            state_ids = self.env['res.country.state'].search(
                [('region', '=', self.region), ('country_id', '=', self.country_id.id)])
        if state_ids:
            for state in state_ids:
                lst.append(state.id)
        result['domain'] = {'state_id': [('id', 'in', lst)]}
        return result

    def write(self, values):
        if self.partner_id:
            if 'pincode' in values:
                pincode_val = values.get('pincode')
                self.partner_id.zip = pincode_val
            if 'city' in values:
                city_val = values.get('city')
                self.partner_id.city = city_val

            if 'street_address' in values:
                street_val = values.get('street_address')
                self.partner_id.street = street_val

            if 'phone_number1' in values:
                phone_val = values.get('phone_number1')
                self.partner_id.phone = phone_val

            if 'country_id' in values:
                country_val = values.get('country_id')
                country_val_id = self.env['res.country'].search([('id', '=', country_val)], limit=1)
                if country_val_id:
                    self.partner_id.country_id = country_val_id.id
                else:
                    self.partner_id.country_id = False

            if 'state_id' in values:
                state_val = values.get('state_id')
                state_val_id = self.env['res.country.state'].search([('id', '=', state_val)], limit=1)
                if state_val_id:
                    self.partner_id.state_id = state_val_id.id
                else:
                    self.partner_id.state_id = False
        res = super(ResUsers, self).write(values)
        return res

    def _compute_journey_names(self):
        for val in self:
            journey_lst = []
            cr = self.env.cr
            cr.execute('SELECT id FROM course_journey')
            jouneys = cr.fetchall()
            if jouneys:
                for row in jouneys:
                    journey_id = self.env['course.journey'].browse(row)
                    if journey_id.journey_channel_partner_ids:
                        for journey_partner in journey_id.journey_channel_partner_ids:
                            if val.partner_id == journey_partner.partner_id:
                                journey_lst.append(journey_id.id)
                val.my_journey_ids = [(6, 0, journey_lst)]
            else:
                val.my_journey_ids = False

    def topic_of_interest_val(self):
        val = ''
        first_topic = False
        if self.topic_of_interest_ids:
            for topic in self.topic_of_interest_ids:
                if not first_topic:

                    val = str(topic.name)
                    first_topic = True
                else:
                    val = val + ',' + str(topic.name)

        return val

    def state_get(self, course_id):
        state_val = ''
        lst = []
        dict = {}
        if course_id:
            channel_id = self.env['slide.channel'].browse(course_id)
            if channel_id:
                if channel_id.sudo().channel_partner_ids:
                    for partner in channel_id.sudo().channel_partner_ids:
                        if self.partner_id.id == partner.partner_id.id:
                            if partner.completion == 100:
                                state_val = 'Completed'
                            else:
                                state_val = 'In Progress'

        return state_val
    
    
    def user_code_get(self,user):
        code=''
        if user.pre_joinee_code:
            code= user.pre_joinee_code

        elif user.emp_code:
            code= user.emp_code
        elif user.customer_code:
            code= user.customer_code
        else:
            code=user.login
            
        return code
    
    
    
    def emp_user_create(self):
        url = 'http://13.126.107.206/HCMVIVEK/FITSCommon/FITSCommon.svc/CommonService'
        
        headers = {
            "CompanyID": "10000",
            "EmployeeID": '44578',
            "UserID": '15153',
            "Password": '123',
            "Apiname": 'NewJoineeAPIData',
            "Content": "application/x-www-form-urlencoded"
          }
        try:
            r = requests.post(url, headers=headers)
            # _logger.info("Auth API Response : %s " % str(r.content))
            j = json.loads(r.text)
        except Exception as e:
            msg = "API Error: %s" %e
            raise UserError(msg)
        
        data = j.get('Data')
        emp_data = eval(data)
        emp_values_lst = emp_data.get('EmployeeData')
        # print ("yyyyyyyy",emp_values)
        # emp_values_lst=[{"Employee Code":"1234343rah","Employee Name":"Rajnnnn","Phone Number":"898998989","Pin Code":"5665885","City":"Kanpur","Country":"IN","State":"Bihar","Address_line1":"aa","Address_line2":"near","Address_line3":"33"},{"Employee Code":"prrr55","Employee Name":"Prasuuuu","Phone Number":"11111111","Pin Code":"2222","City":"Dehradun","Country":"IN","State":"Uttarakhand","Address_line1":"siddhut","Address_line2":"near","Address_line3":"33"}]
        
        cr = self.env.cr
        cr.execute('SELECT id FROM res_users where  is_employee = %s',
                   (True,))
        user_ids = cr.fetchall()
        emp_code_lst=[]
        for user in user_ids:
            user_id= self.env['res.users'].browse(user)
            if user_id.emp_code:
               emp_code_lst.append(user_id.emp_code) 
        
        for emp in emp_values_lst:
            empl_code = emp['Employee Code']
            if empl_code not in emp_code_lst:
                add1=''
                add2=''
                add3=''
                if emp['Address_line1']:
                    add1= emp['Address_line1']
                    
                if emp['Address_line2']:
                    add2= emp['Address_line2']
                    
                if emp['Address_line3']:
                    add3= emp['Address_line3']
                emp_address= add1+' '+add2+' '+add3
                country_id= False
                state_id=False
                if emp['Country']:
                    country=self.env['res.country'].search([('code','=',emp['Country'])],limit=1)
                    if country:
                        country_id=country.id
                        
                if emp['State']:
                    state=self.env['res.country.state'].search([('code','=',emp['Country'])],limit=1)
                    if state:
                        state_id=state.id
                self.env['res.users'].create({'name':emp['Employee Name'],'login':emp['Employee Name'],'emp_code':emp['Employee Code'],'phone_number1':emp['Phone Number'],'is_employee':True,
                                              'street_address':emp_address,'city':emp['City'],'pincode':emp['Pin Code'],'country_id':country_id,'state_id':state_id,
                                              })
            else:
                usr_id= self.env['res.users'].search([('emp_code','=',empl_code)],limit=1)
                add1=''
                add2=''
                add3=''
                if emp['Address_line1']:
                    add1= emp['Address_line1']
                    
                if emp['Address_line2']:
                    add2= emp['Address_line2']
                    
                if emp['Address_line3']:
                    add3= emp['Address_line3']
                emp_address= add1+' '+add2+' '+add3
                country_id= False
                state_id=False
                if emp['Country']:
                    country=self.env['res.country'].search([('code','=',emp['Country'])],limit=1)
                    if country:
                        country_id=country.id
                        
                if emp['State']:
                    state=self.env['res.country.state'].search([('code','=',emp['State'])],limit=1)
                    if state:
                        state_id=state.id
                if usr_id:
                    usr_id.name=emp['Employee Name']
                    usr_id.login=emp['Employee Name']
                    usr_id.emp_code=emp['Employee Code']
                    usr_id.phone_number1=emp['Phone Number']
                    usr_id.street_address=emp_address
                    usr_id.city=emp['City']
                    usr_id.pincode=emp['Pin Code']
                    
                    usr_id.country_id=country_id
                    usr_id.state_id=state_id
                    
        return True
        

    # @api.depends('is_employee')
    # def get_is_employee(self):
    #     for rec in self:
    #         if rec.is_employee:
    #             if not rec.employee_code:
    #                 emp_code = code = ''.join(random.choices(string.ascii_uppercase +
    #                                                  string.digits, k=8))
    #             else:
    #                 emp_code=rec.employee_code
    #         else:
    #             emp_code=''
    #         rec.employee_code=emp_code
    #
    #
    # @api.onchange('is_employee')
    # def onchange_is_employee(self):
    #     if self.is_employee:
    #         code= ''.join(random.choices(string.ascii_uppercase +
    #                                                  string.digits, k=8))
    #         self.emp_code=code
    #
    #     else:
    #         self.emp_code=''
    #
    #

    def lang_val(self):
        val = ''
        first_bool = False
        if self.lang:
            val = ''
            if self.lang == 'en_IN':
                val = 'English'
            if self.lang == 'hi_IN':
                val = 'Hindi'

            if self.lang == 'gu_IN':
                val = 'Gujarati'

            if self.lang == 'te_IN':
                val = 'Telugu'

            if self.lang == 'ma_IN':
                val = 'Malyalam'

            if self.lang == 'assa_IN':
                val = 'Assamese'

            if self.lang == 'ta_IN':
                val = 'Tamil'

            if self.lang == 'ka_IN':
                val = 'Kannada'

            if self.lang == 'mal_IN':
                val = 'Malyalam'

        return val

    def course_delay_inprogress_method(self):
        header_label_list = ["Course Name", "Due Date", "User"]
        current_date = datetime.now()
        template_id = self.env.ref('ecom_lms.email_template_delay_inprogress_course_lst')
        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        user_ids = self.env['res.users'].search([])

        user_dict = {}

        for user in user_ids:

            string = 'Delayed In progress Course List'
            wb = xlwt.Workbook(encoding='utf-8')
            worksheet = wb.add_sheet(string)
            filename = 'Delayed Course List' + '.xls'
            style_value = xlwt.easyxf(
                'font: bold on, name Arial ,colour_index black;')
            style_header = xlwt.easyxf(
                'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

            worksheet.write_merge(0, 0, 0, 5, "Delayed In progress Course List", xlwt.easyxf(
                'font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))

            worksheet.write(1, 0, 'User Name', style_value)
            worksheet.write(1, 1, 'Course Name', style_value)
            # worksheet.write(1, 1, 'Due Date', style_value)
            worksheet.write(1, 2, 'Due Date', style_value)
            # worksheet.write(1, 1, 'Close Date', style_value)
            a = 2

            chaneel_lst = []
            channel_partner_ids = self.env['slide.channel.partner'].search([('partner_id', '=', user.partner_id.id)])
            for channel_partner in channel_partner_ids:
                if channel_partner.completion != 100:
                    if channel_partner.channel_id.course_close_date:
                        if channel_partner.channel_id.course_close_date.date() < current_date.date():
                            if channel_partner.channel_id.id not in chaneel_lst:
                                chaneel_lst.append(channel_partner.channel_id.id)

            channel_ids = self.env['slide.channel'].sudo().browse(chaneel_lst)

            for channel in channel_ids:
                due_date = ''
                due_date = channel.course_close_date.strftime('%d-%m-%Y')
                worksheet.write(a, 0, user.name or '')
                worksheet.write(a, 1, channel.name or '')
                worksheet.write(a, 2, due_date or '')
                a = a + 1

            fp = io.BytesIO()
            wb.save(fp)
            out = base64.encodestring(fp.getvalue())
            view_report_status_id = self.env['delayed.course.inprogress.list.view.report'].create(
                {'excel_file': out, 'file_name': filename})

            attachment_id = self.env['ir.attachment'].create({'name': 'Delayed In Progress Course List.xlsx',
                                                              'store_fname': filename,
                                                              'datas': out})

            user_dict[user.id] = attachment_id.id

        for usr in user_dict:
            usr_mail_id = self.env['res.users'].browse(usr)
            att_id = self.env['ir.attachment'].browse(user_dict[usr])
            template_id.email_to = usr_mail_id.partner_id.email
            template_id.attachment_ids = [(6, 0, [att_id.id])]
            template_id.send_mail(self.id, force_send=True)

    # @api.model
    # def default_get(self, fields):
    #     res = super(ResUsers, self).default_get(fields)
    #     vals = [(0, 0, {'role_id': 6})]
    #     res.update({'role_line_ids': vals})
    #     return res


class delayed_course_inprogress_list_view_report(models.TransientModel):
    _name = 'delayed.course.inprogress.list.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
    
    
    
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res = {'db': self.env.cr.dbname}
        if partner.signup_valid:
            res['token'] = token
            res['name'] = partner.name
        if partner.user_ids:
            code=''
            if partner.user_ids[0].pre_joinee_code:
                code= partner.user_ids[0].pre_joinee_code
    
            elif partner.user_ids[0].emp_code:
                code= partner.user_ids[0].emp_code
            elif partner.user_ids[0].customer_code:
                code= partner.user_ids[0].customer_code
            else:
                code=partner.user_ids[0].login
            # res['login'] = partner.user_ids[0].login
            res['login'] =code
        else:
            res['email'] = res['login'] = partner.email or ''
        return res


    # @api.model
    # def default_get(self, fields):
    #     res = super(ResUsers, self).default_get(fields)
    #     vals_new=self.env['res.users.role'].sudo().search([('name','=','Customer Role')])
    #     res_new_id=vals_new.id
    #     vals = [(0, 0, {'role_id': res_new_id})]
    #     res.update({'role_line_ids': vals})
    #     return res



    
class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to a attachment
        if not (self.env.is_admin() or self.env.user.has_group('base.group_user') or self.env.user.has_group('base.group_portal')):
            raise AccessError(_("Sorry, you are not allowed to access this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)            # {model_name: set(ids)}
        if self:
            # DLE P173: `test_01_portal_attachment`
            self.env['ir.attachment'].flush(['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute('SELECT res_model, res_id, create_uid, public, res_field FROM ir_attachment WHERE id IN %s', [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
                if not self.env.is_system() and res_field:
                    raise AccessError(_("Sorry, you are not allowed to access this document."))
                if public and mode == 'read':
                    continue
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list of writeable fields
                # e.g. in the case of a user inserting an image into his image signature
                # we need to bypass this check which would needlessly throw us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)
            
            
    
    
    