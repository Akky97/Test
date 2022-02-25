from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class PartnerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):
        print ("line----->", lines)
        print ("line model id----->", lines.id)
        print ("line user id----->", lines.user_id.name)
        print ("line write_uid ----->", lines.write_uid.name)
        print ("line report_date ----->", lines.report_date)
        print ("line create_date ----->", lines.create_date)
        print ("line write_date ----->", lines.write_date)
        print ("3")
        # for obj in lines:
        report_name = "sheet 1"
        report_head = 'User Report'
        print ("data---->", data)

        arr = []
        for i in lines:
            val = {
                # "s.no": no,
                "user": i['user_id']['name'],
                "date": i['report_date'],
                "c_user": i['create_uid']['name'],
                "w_date": i['write_date'],
                "c_date": i['create_date'],
                "id": i['id'],
            }
            arr.append(val)
        print (arr)


        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter','font_color': 'white', 'fg_color': 'black'})
        bold = workbook.add_format({'bold': True})
        align_left = workbook.add_format({'align': 'left'})

        sheet.write(1, 0, ('Sl.no'), bold)
        sheet.write(1, 1, ('User'), bold)
        sheet.write(1, 2, ('Date'), bold)
        sheet.write(1, 3, ('Write User'), bold)
        sheet.write(1, 4, ('Write Date'), bold)
        sheet.write(1, 5, ('Create Date'), bold)
        sheet.write(1, 6, ('Id'), bold)
    

        # increasing width of column
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.merge_range('A1:G1', report_head, merge_format)
        row = 2
        s_no = 1
        for res in arr:
            sheet.write(row, 0, s_no, align_left)
            sheet.write(row, 1, res['user'])
            sheet.write(row, 2, res['date'])
            sheet.write(row, 3, res['c_user'])
            sheet.write(row, 4, res['w_date'])
            sheet.write(row, 5, res['c_date'])
            sheet.write(row, 6, res['id'], align_left)
            row = row + 1
            s_no = s_no + 1

            print ("Array printed for s.no :", s_no - 1)

        print ("Report Printed")

PartnerXlsx('report.clickbima.res_partner.xlsx', 'create.report')