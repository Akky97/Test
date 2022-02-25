from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from re import search
import numpy as np

class reconcile(models.Model):
    _name = 'reconcile'

    name = fields.Char()
    type = fields.Selection([('insurername', 'Insurer Name')], default='', string="Type: " )
    fiscal_year = fields.Many2one('fyyear', string="Financial Year: ",default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],limit=1).id,required=True)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),('01-12', 'December')],string="Month")
    insurer_name = fields.Many2one('res.partner', string="Insurer Name :",
                                   domain=[('customer', '=', True), ('is_company', '=', True)],required=True)
    insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch :",required=True)
    round_no = fields.Char(string="RoundOff: ")
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    clientname = fields.Many2one('res.partner', string="Client Name")
    comm_stat_one2many = fields.One2many('reconcile_comm_details','reconcile_comm_id')
    pol_trans_one2many = fields.One2many('reconcile_pol_details','reconcile_pol_id')
    main_stat_one2many = fields.One2many('reconcile_main_details','reconcile_main_id')
    comm_status = fields.Selection([('yes', 'yes'), ('no', 'no')])
    poly_status = fields.Selection([('yes', 'yes'), ('no', 'no')])

    @api.multi
    @api.onchange('insurer_name')
    def compute_ptransaction1(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.insurer_name.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'insurer_branch': [('id', 'in', temp)]})
        return res

    @api.onchange('monthly', 'months', 'fiscal_year')
    def onchange_monthly(self):
        import odoo
        import datetime
        if self.monthly:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            print(end_year, "end")
            start_year1 = self.fiscal_year.date_start
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year
            print(start_year, "start")
            if (self.monthly == 'yearly'):
                self.date_from = str(self.fiscal_year.date_start)
                self.date_to = str(self.fiscal_year.date_end)
            elif (self.monthly == 'monthly'):
                if self.months == '01-01':
                    self.start_year = start_year
                    self.end_year = end_year
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')
                    self.date_from = str(jan_start)
                    self.date_to = str(jan_end)
                    print(end_year)

                if self.months == '01-02':
                    self.start_year = start_year
                    self.end_year = end_year
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    self.date_from = str(feb_start)
                    self.date_to = str(feb_end)

                if self.months == '01-03':
                    self.start_year = start_year
                    self.end_year = end_year
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    self.date_from = str(mar_start)
                    self.date_to = str(mar_end)

                if self.months == '01-04':
                    self.start_year = start_year
                    self.end_year = end_year
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    self.date_from = str(apr_start)
                    self.date_to = str(apr_end)

                if self.months == '01-05':
                    self.start_year = start_year
                    self.end_year = end_year
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    self.date_from = str(may_start)
                    self.date_to = str(may_end)

                if self.months == '01-06':
                    self.start_year = start_year
                    self.end_year = end_year
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    self.date_from = str(june_start)
                    self.date_to = str(june_end)

                if self.months == '01-07':
                    self.start_year = start_year
                    self.end_year = end_year
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    self.date_from = str(jul_start)
                    self.date_to = str(jul_end)

                if self.months == '01-08':
                    self.start_year = start_year
                    self.end_year = end_year
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    self.date_from = str(aug_start)
                    self.date_to = str(aug_end)

                if self.months == '01-09':
                    self.start_year = start_year
                    self.end_year = end_year
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    self.date_from = str(sep_start)
                    self.date_to = str(sep_end)

                if self.months == '01-10':
                    self.start_year = start_year
                    self.end_year = end_year
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    self.date_from = str(oct_start)
                    self.date_to = str(oct_end)

                if self.months == '01-11':
                    self.start_year = start_year
                    self.end_year = end_year
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    self.date_from = str(nov_start)
                    self.date_to = str(nov_end)

                if self.months == '01-12':
                    self.start_year = start_year
                    self.end_year = end_year
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    self.date_from = str(dec_start)
                    self.date_to = str(dec_end)
        else:
            pass

    @api.onchange('quarter', 'fiscal_year')
    def onchange_quarter(self):
        import odoo
        import datetime
        if self.quarter:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            print(end_year, "end")
            start_year1 = self.fiscal_year.date_start
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year
            print(start_year, "start")
            if (self.quarter == 'q1'):
                self.start_year = start_year
                self.end_year = end_year
                q1_start = str(start_year) + str('-04-01')
                q1_end = str(start_year) + str('-06-30')
                self.date_from = str(q1_start)
                self.date_to = str(q1_end)
            elif (self.quarter == 'q2'):
                self.start_year = start_year
                self.end_year = end_year
                q2_start = str(start_year) + str('-07-01')
                q2_end = str(start_year) + str('-09-30')
                self.date_from = str(q2_start)
                self.date_to = str(q2_end)
            elif (self.quarter == 'q3'):
                self.start_year = start_year
                self.end_year = end_year
                q3_start = str(start_year) + str('-10-01')
                q3_end = str(start_year) + str('-12-31')
                self.date_from = str(q3_start)
                self.date_to = str(q3_end)
            elif (self.quarter == 'q4'):
                self.start_year = start_year
                self.end_year = end_year
                q4_start = str(end_year) + str('-01-01')
                q4_end = str(end_year) + str('-03-31')
                self.date_from = str(q4_start)
                self.date_to = str(q4_end)
            else:
                pass

    def match_reco(self):
        insurer_name=self.insurer_name.id
        insurer_branch=self.insurer_branch.id
        client_name=self.clientname.name
        fy=self.fiscal_year.id
        if not fy:
            raise ValidationError(_('Please Select the Fiscal Year'))
        if not insurer_name :
            raise ValidationError(_('Please Select the Insurer Name'))
        if not insurer_branch:
            raise ValidationError(_('Please Select the Insurer Branch'))
        try:
            policy_trans_records = self.env['policytransaction'].search(
                [('insurername123', '=', insurer_name), ('insurerbranch', '=', insurer_branch), ('fy', '=', fy)])
            commission_records = self.env['reconcile.reconcile'].search(
                [('insurername123', '=', insurer_name), ('insurerbranch', '=', insurer_branch), ('fiscal_year', '=', fy)])
            count_matched = 0

            for j in commission_records:
                for i in policy_trans_records:
                    if j.reconcile_status == 'new' or j.reconcile_status == 'unmatched':
                        if i.startfrom == j.startfrom:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'Start Date  matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'Start Date not matched'}]]})
                            error.write({"reconcile_error": 'Start Date not matched'})
                            count_matched += 1
                            
                        if i.insurername123.id == j.insurername123.id:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'Insurer Name matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'Insurer Name not matched'}]]})
                            error.write({"reconcile_error": 'Insurer Name not matched'})
                            count_matched += 1

                        if i.insurerbranch.id == j.insurerbranch.id:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'Insurer Branch matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'Insurer Branch not matched'}]]})
                            error.write({"reconcile_error": 'Insurer Branch not matched'})
                            count_matched += 1

                        if i.fy.id == j.fiscal_year.id:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'Fiscal Year matched'}]]})

                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'Fiscal Year not matched'}]]})
                            error.write({"reconcile_error": 'Fiscal Year not matched'})
                            count_matched += 1

                        if i.clientname.name == j.clientname:
                            error = self.env['reconcile.reconcile'].search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'Client Name matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'Client Name not matched'}]]})
                            error.write({"reconcile_error": 'Client Name not matched'})
                            count_matched += 1

                        if i.brokerage and j.brokerage:
                            diff = i.brokerage - j.brokerage
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'IRDA Brokerage not matched'}]]})
                                error.write({"reconcile_error": 'IRDA Brokerage not matched'})
                                count_matched += 1
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_matched': 'IRDA Brokerage matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [[0, 0, {'error_unmatched': 'IRDA Brokerage not matched'}]]})
                            error.write({"reconcile_error": 'IRDA Brokerage not matched'})
                            count_matched += 1
                        if i.commssionamt and j.commssionamt:
                            diff = i.commssionamt - j.commssionamt
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'IRDA Commission Amount not matched'}]]})
                                error.write({"reconcile_error": 'IRDA Commission Amount not matched'})
                                count_matched += 1
                            else:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write(
                                    {"reconcile_error_id": [[0, 0, {'error_matched': 'IRDA Commission Amount  matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write(
                                {"reconcile_error_id": [[0, 0, {'error_unmatched': 'IRDA Commission Amount not matched'}]]})
                            error.write({"reconcile_error": 'IRDA Commission Amount not matched'})
                            count_matched += 1

                        if i.netcomm and j.netcomm:
                            diff = i.netcomm - j.netcomm
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'IRDA Net Commission Amount not matched'}]]})
                                error.write({"reconcile_error": 'IRDA Net Commission Amount not matched'})
                                count_matched += 1
                            else:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'IRDA Net Commission Amount matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write({"reconcile_error_id": [
                                [0, 0, {'error_unmatched': 'IRDA Net Commission Amount not matched'}]]})
                            error.write({"reconcile_error": 'IRDA Net Commission Amount not matched'})
                            count_matched += 1

                        if i.broprem and j.broprem:
                            diff = i.broprem - j.broprem
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'Rewards Brokerage not matched'}]]})
                                error.write({"reconcile_error": 'Rewards Brokerage not matched'})
                                count_matched += 1
                            else:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write(
                                    {"reconcile_error_id": [[0, 0, {'error_matched': 'Rewards Brokerage matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write(
                                {"reconcile_error_id": [[0, 0, {'error_unmatched': 'Rewards Brokerage not matched'}]]})
                            error.write({"reconcile_error": 'Rewards Brokerage not matched'})
                            count_matched += 1

                        if i.commamt and j.commamt:
                            diff = i.commamt - j.commamt
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'Rewards Commission not matched'}]]})
                                error.write({"reconcile_error": 'Rewards Commission not matched'})
                                count_matched += 1
                            else:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write(
                                    {"reconcile_error_id": [[0, 0, {'error_matched': 'Rewards Commission matched'}]]})

                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write(
                                {"reconcile_error_id": [[0, 0, {'error_unmatched': 'Rewards Commission not matched'}]]})
                            error.write({"reconcile_error": 'Rewards Commission not matched'})
                            count_matched += 1

                        if i.netcommission and j.netcommission:
                            diff = i.netcommission - j.netcommission
                            if diff >= 0.99:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write({"reconcile_error_id": [
                                    [0, 0, {'error_unmatched': 'Rewards Net Commission not matched'}]]})
                                error.write({"reconcile_error": 'Rewards Commission not matched'})
                                count_matched += 1
                            else:
                                error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                                error.write(
                                    {"reconcile_error_id": [[0, 0, {'error_matched': 'Rewards Net Commission matched'}]]})
                        else:
                            error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                            error.write(
                                {"reconcile_error_id": [[0, 0, {'error_unmatched': 'Rewards Net Commission not matched'}]]})
                            error.write({"reconcile_error": 'Rewards Commission not matched'})
                            count_matched += 1

                    if count_matched != 0:
                        error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                        error.write({"reconcile_status": 'unmatched'})
                    else:
                        error = self.env['reconcile.reconcile'].sudo().search([('id', '=', j.id)], limit=1)
                        error.write({"reconcile_status": 'matched'})
                        error.write({"policy_transaction_id": i.id})
        except Exception as e:
            raise ValidationError(_('Something went wrong !'))

    def fetch_comm(self):
        # if self.comm_status =='yes':
        #     raise ValidationError(_('Already Fetched'))
        # else:
        self.comm_stat_one2many.unlink()
        comm_stat = self.env['reconcile.reconcile'].sudo().search(
            [('insurername123', '=', self.insurer_name.id), ('insurerbranch', '=', self.insurer_branch.id),
             ('date_from', '=', self.date_from), ('date_to', '=', self.date_to)])
        if comm_stat:
            eo = []
            for i in comm_stat:
                print(i.clientname, "IIiiiiiii")
                eo.append([0, 0, {"clientname": i.clientname,
                                  "start_date": i.startfrom,
                                  "expiry_date": i.expiry,
                                  "irda_commssionamt": i.commssionamt,
                                  "irda_commssion_per": i.rate,
                                  "net_premium_amount": i.brokerageprem,
                                  "policy_comm": i.policyno1,
                                  "comm_pk_id": i.id}])
            self.sudo().write({"comm_status": "yes", "comm_stat_one2many": eo})
            message_id = self.env['message.wizard'].sudo().create(
                {'text': 'Successfully Fetched Commission Statement'})
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                # pass the id
                'res_id': message_id.id,
                'target': 'new'
            }



    def fetch_pol(self):
        # if self.poly_status =='yes':
        #     raise ValidationError(_('Already Fetched'))
        # else:
        self.pol_trans_one2many.unlink()
        pol_stat = self.env['policytransaction'].sudo().search(
            [('insurername123', '=', self.insurer_name.id), ('insurerbranch', '=', self.insurer_branch.id),
             ('startfrom', '>=', self.date_from), ('startfrom', '<=', self.date_to)], order='startfrom asc')
        eo = []
        if pol_stat:
            for i in pol_stat:
                eo.append([0, 0, {"clientname_pol": i.clientname.name,
                                  "start_date_pol": i.startfrom,
                                  "expiry_date_pol": i.expiry,
                                  "irda_commssionamt_pol": i.commssionamt,
                                  "irda_commssion_per_pol": i.rate,
                                  "net_premium_amount_pol": i.brokerageprem,
                                  "policy_pol": i.policyno,
                                  "pol_pk_id": i.id}])
            self.sudo().write({'poly_status': "yes", 'pol_trans_one2many': eo})
            message_id = self.env['message.wizard'].sudo().create(
                {'text': 'Successfully Fetched Policy Statement'})
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                # pass the id
                'res_id': message_id.id,
                'target': 'new'
            }

    def reconcile_matched(self):
        comm_stat = self.env['reconcile'].sudo().search([('id', '=', self.id)])
        comm_stat.main_stat_one2many.unlink()
        iv=[]
        jv=[]

        for i in comm_stat.comm_stat_one2many:
            m = 1
            for j in comm_stat.pol_trans_one2many:
                i_values ={"clientname":i.clientname.lower(),
                           "policy_comm":i.policy_comm,
                           "irda_commssionamt":i.irda_commssionamt,
                           "irda_commssion_per":i.irda_commssion_per,
                           "net_premium_amount":i.net_premium_amount,
                           "start_date":i.start_date,
                           "expiry_date":i.expiry_date,
                           }
                j_values ={"clientname":j.clientname_pol.lower(),
                           "policy_comm": j.policy_pol,
                           "irda_commssionamt": j.irda_commssionamt_pol,
                           "irda_commssion_per": j.irda_commssion_per_pol,
                           "net_premium_amount": j.net_premium_amount_pol,
                           "start_date": j.start_date_pol,
                           "expiry_date": j.expiry_date_pol,
                           }
                if i_values == j_values:
                    self.matched_datas(i_values,"matched",j)
                    break

                # elif ((str.__contains__(str(i_values['clientname']),str(j_values['clientname'])))) or i_values['clientname'] == str(j_values['clientname']) or search(i_values['clientname'],j_values['clientname']):
                #
                #     if (j_values['policy_comm']) ==False or  (i_values['policy_comm']) ==False :
                #         pass
                #     else:
                #         if ((str.__contains__(str(i_values['policy_comm']),str(j_values['policy_comm'])))) or str(i_values['policy_comm']) == str(j_values['policy_comm']) or search((i_values['policy_comm']).replace('\\',""),(j_values['policy_comm'])):
                #
                #             if (int(i_values['net_premium_amount'])) == (int(j_values['net_premium_amount'])) or (round(i_values['net_premium_amount'])) == (round(j_values['net_premium_amount'])):
                #                 self.matched_datas(i_values,"rmatch",j)
                #                 break
                #
                #             else:
                #                 self.matched_data(i_values, "pmatch")
                #                 break
                #
                #         else:
                #             if (m == len(comm_stat.pol_trans_one2many)):
                #                 self.matched_data(i_values, "pmatch")
                #                 break

                elif ((str.__contains__(str(i_values['clientname']), str(j_values['clientname'])))) or i_values['clientname'] == str(j_values['clientname']) or search(i_values['clientname'],j_values['clientname']):
                    if int(i_values['net_premium_amount']) ==  int(j_values['net_premium_amount']) or (i_values['net_premium_amount']) == (j_values['net_premium_amount']):
                        if int(i_values['irda_commssionamt']) == int(j_values['irda_commssionamt']) or i_values['irda_commssionamt'] == j_values['irda_commssionamt'] :
                            self.matched_datas(i_values, "matched", j)
                            break
                        else:
                            self.matched_datas(i_values,"pmatch",j)
                            break
                    elif (int(i_values['net_premium_amount'])) == (int(j_values['net_premium_amount'])) or (round(i_values['net_premium_amount'])) == (round(j_values['net_premium_amount'])):
                        self.matched_datas(i_values, "rmatch", j)
                        break
                    else:
                        if (m == len(comm_stat.pol_trans_one2many)):
                            self.matched_datas(i_values,"pmatch",j)
                            break
                else:
                    if(m==len(comm_stat.pol_trans_one2many)):
                        self.matched_datas(i_values, "amatch",i)
                        break
                m += 1

        for z in comm_stat.pol_trans_one2many:
           n= 1
           for k in comm_stat.comm_stat_one2many:
                i_values ={"clientname":k.clientname.lower(),
                           "policy_comm":k.policy_comm,
                           "irda_commssionamt":k.irda_commssionamt,
                           "irda_commssion_per":k.irda_commssion_per,
                           "net_premium_amount":k.net_premium_amount,
                           "start_date":k.start_date,
                           "expiry_date":k.expiry_date
                           }

                j_values ={"clientname":z.clientname_pol.lower(),
                           "policy_comm": z.policy_pol,
                           "irda_commssionamt": z.irda_commssionamt_pol,
                           "irda_commssion_per": z.irda_commssion_per_pol,
                           "net_premium_amount": z.net_premium_amount_pol,
                           "start_date": z.start_date_pol,
                           "expiry_date": z.expiry_date_pol,
                           }
                if i_values == j_values:
                    # self.matched_datas(i_values,"matched",j)
                    break
                elif ((str.__contains__(str(i_values['clientname']), str(j_values['clientname'])))) or i_values['clientname'] == str(j_values['clientname']) or search(i_values['clientname'],j_values['clientname']):

                    if (j_values['policy_comm']) == False or (i_values['policy_comm']) == False:
                        pass
                    else:
                        if ((str.__contains__(str(i_values['policy_comm']), str(j_values['policy_comm'])))) or str(i_values['policy_comm']) == str(j_values['policy_comm']) or search((i_values['policy_comm']).replace('\\', ""), (j_values['policy_comm'])):

                            if (int(i_values['net_premium_amount'])) == (int(j_values['net_premium_amount'])) or (round(i_values['net_premium_amount'])) == (round(j_values['net_premium_amount'])):
                                # print("1")
                                # self.matched_datas(i_values,"rmatch")
                                break
                            else:
                                # print("2")
                                # self.matched_data(i_values, "pmatch")
                                break
                        else:
                            # if (n == len(comm_stat.pol_trans_one2many)):
                            #     print("3")
                                # self.matched_data(j_values, "smatch")
                                break
                else:
                    # if (n == len(comm_stat.pol_trans_one2many)):
                    #     print("4")
                        self.matched_datas(j_values, "smatch",z)
                        break









        message_id = self.env['message.wizard'].sudo().create({'text': 'Successfully Reconciled'})
        return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                # pass the id
                'res_id': message_id.id,
                'target': 'new'
            }


    def lock_reco(self):
        message_id = self.env['message.wizard'].sudo().create(
            {'text': 'Successfully lock the file'})
        return {
            'name': 'Message',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            # pass the id
            'res_id': message_id.id,
            'target': 'new'
        }




    def matched_data(self,i_values,status):
        partially = []
        partially.append([0, 0, {"clientname": i_values['clientname'],
                                 "policy_comm": i_values['policy_comm'],
                                 "irda_commssionamt": i_values['irda_commssionamt'],
                                 "irda_commssion_per": i_values['irda_commssion_per'],
                                 "net_premium_amount": i_values['net_premium_amount'],
                                 "start_date": i_values['start_date'],
                                 "expiry_date": i_values['expiry_date'],
                                 "status":status,

                                 }])
        self.sudo().write({'main_stat_one2many': partially})

    def matched_datas(self,i_values,status,j_values):
        partially = []
        partially.append([0, 0, {"clientname": i_values['clientname'],
                                 "policy_comm": i_values['policy_comm'],
                                 "irda_commssionamt": i_values['irda_commssionamt'],
                                 "irda_commssion_per": i_values['irda_commssion_per'],
                                 "net_premium_amount": i_values['net_premium_amount'],
                                 "start_date": i_values['start_date'],
                                 "expiry_date": i_values['expiry_date'],
                                 "status":status,
                                 "match_number":j_values.line_no,

                                 }])
        self.sudo().write({'main_stat_one2many': partially})
class reconcile_comm_details(models.Model):
    _name='reconcile_comm_details'

    reconcile_comm_id =fields.Many2one('reconcile',ondelete='cascade', index=True)
    clientname = fields.Char(string="Client Name")
    policy_comm=fields.Char(string="Policy No.")
    irda_commssionamt =fields.Float(string="IRDA commission")
    irda_commssion_per =fields.Float(string="IRDA commission(%)")
    net_premium_amount =fields.Float(string="Amount")
    start_date =fields.Date(string="Start Date")
    expiry_date =fields.Date(string="Expiry Date")
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")
    status=fields.Selection([('yes','yes'),('no','no')])
    comm_pk_id =fields.Many2one('reconcile.reconcile')

    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.reconcile_comm_id.comm_stat_one2many:
                line_rec.line_no = line_num
                line_num += 1


class reconcile_pol_details(models.Model):
    _name='reconcile_pol_details'


    reconcile_pol_id =fields.Many2one('reconcile',ondelete='cascade', index=True)
    clientname_pol = fields.Char(string="Client Name")
    policy_pol = fields.Char(string="Policy No.")
    irda_commssionamt_pol = fields.Float(string="IRDA commission")
    irda_commssion_per_pol = fields.Float(string="IRDA commission(%)")
    net_premium_amount_pol = fields.Float(string="Amount")
    start_date_pol = fields.Date(string="Start Date")
    expiry_date_pol = fields.Date(string="Expiry Date")
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")
    status = fields.Selection([('yes', 'yes'), ('no', 'no')])
    pol_pk_id = fields.Many2one('policytransaction', string="PolID")

    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.reconcile_pol_id.pol_trans_one2many:
                line_rec.line_no = line_num
                line_num += 1


class reconcile_main_details(models.Model):
    _name='reconcile_main_details'

    reconcile_main_id =fields.Many2one('reconcile',ondelete='cascade', index=True)
    clientname = fields.Char(string="Client Name")
    policy_comm=fields.Char(string="Policy No.")
    irda_commssionamt =fields.Float(string="IRDA commission")
    irda_commssion_per =fields.Float(string="IRDA commission(%)")
    net_premium_amount =fields.Float(string="Amount")
    start_date =fields.Date(string="Start Date")
    expiry_date =fields.Date(string="Expiry Date")
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")
    status = fields.Selection([('matched','Matched'),('unmatch','Unmatch'),('amatch','Excess Entry'),('smatch','Short Entry'),('pmatch','Partially Matched'),('rmatch','Round Matched'),('fmatch','Forcefully Matched')])
    match_number = fields.Integer()

    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.reconcile_main_id.main_stat_one2many:
                line_rec.line_no = line_num
                line_num += 1
