
from datetime import datetime,timedelta
from decimal import Decimal

import xlsxwriter
import psycopg2
from psycopg2.extras import RealDictCursor
import os.path
from os import path
import uuid
import config
import sys
import logging
import json

logging.basicConfig(filename='leave_summary_report.log', format='%(name)s - %(levelname)s - %(message)s')

def main(argv):
    try:
        print("mainargs"+str(argv))
        if len(sys.argv) != 2:
            print("Usage: python3 service.py <pid>")
            sys.exit(1)
        else:

            pid = sys.argv[1:]
            leave_report_generate(pid[0])

    except Exception as e:
        print("mainargserror"+str(e))


def updateStatus(connection,status,public_id,file_path):

    try:

        query = connection.cursor(cursor_factory=RealDictCursor)
        print('File Update Status :  ' +str(status))
        update_query = "Update tbl_report_downloads set status="+str(status)+" ,file_path = '"+str(file_path)+"' where public_id='" + str(public_id) +"' and \"isActive\" =1"
        query.execute(update_query)
        connection.commit()
        query.close()

    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def leave_report_generate(pid):

    try:

        UploadFilePath = config.UploadFilePath
        connection = psycopg2.connect(user=config.postgresusername,
                                      password=config.postgrespassword,
                                      host=config.host,
                                      port=config.port,
                                      database=config.database)

        try:
            query = connection.cursor(cursor_factory=RealDictCursor)

            select_query_string = "select * from tbl_report_downloads where public_id='" + str(
                pid) + "' and \"isActive\" =1"
            query.execute(select_query_string)
            report_details = query.fetchall()


            year = report_details[0]['year']
            month = report_details[0]['month']

            updateStatus(connection,1,pid,'')

            leave_type_obj = {"1": "AL", "2": "MC", "3": "CL"}
            leave_type_json = json.dumps(leave_type_obj)
            leave_type_data = json.loads(leave_type_json)

            filename=str(uuid.uuid4())+".xlsx"
            filePath=UploadFilePath +"/summary_report"

            if path.exists(filePath):
                filePath=filePath+"/"+filename
            else:
                if not path.exists(UploadFilePath):
                    os.mkdir(UploadFilePath)
                os.mkdir(filePath)
                filePath = filePath + "/" + filename

            # Create a workbook and add a worksheet.
            workbook = xlsxwriter.Workbook(filePath)
            worksheet = workbook.add_worksheet()

            # Add a bold format to use to highlight cells.
            bold = workbook.add_format({'bold': 1})

            # Add a number format for cells with money.
            money_format = workbook.add_format({'num_format': '$#,##0'})

            # Add an Excel date format.
            date_format = workbook.add_format({'num_format': 'mm-dd-yyyy'})
            date_format.set_align('left')
            # Adjust the column width.
            worksheet.set_column(1, 1, 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('M:M', 20)
            cell_format = workbook.add_format()
            cell_format.set_align('left')

            header_cell_format = workbook.add_format({'bold': True})
            header_cell_format.set_align('left')

            row = 0
            column = 0

            # Write some data headers.
            worksheet.write(row,column, 'NO', header_cell_format)
            worksheet.write(row,column+1, 'RKP', header_cell_format)
            worksheet.write(row,column+2, 'START OF EMPLOYMENT', header_cell_format)
            worksheet.write(row,column+3, 'MEDICAL LEAVE ALLOCATION', header_cell_format)
            worksheet.write(row,column+4, 'MC TAKEN', header_cell_format)
            worksheet.write(row,column+5, 'MC LEAVE BALANCE', header_cell_format)
            worksheet.write(row,column+6, 'ANNUAL LEAVE BALANCE BROUGHT FWD (A)', header_cell_format)
            worksheet.write(row,column+7, 'LEAVE ALLOCATED', header_cell_format)
            worksheet.write(row,column+8, 'TOTAL LEAVE', header_cell_format)
            worksheet.write(row,column+9, 'LEAVE TAKEN', header_cell_format)
            worksheet.write(row,column+10, 'BALANCE', header_cell_format)
            worksheet.write(row,column+11, 'UNPAID LEAVE', header_cell_format)


            column_index = 11

            day = timedelta(days=1)
            date1 = datetime(int(year), int(month), 1)
            d = date1
            dates_header = []
            while d.month == int(month):
                dates_header.append(d.strftime('%d - %b'))
                d += day

            d = date1
            dates = []
            while d.month == int(month):
                dates.append(d.strftime('%d-%m-%Y'))
                d += day

            for date_value in  dates_header:
                column_index = column_index + 1
                worksheet.write(row, column+column_index, date_value, header_cell_format)


            # Start from the first cell below the headers.

            row = row + 1
            serial_no = 0
            leave_summary_query = "SELECT * FROM tbluser LEFT OUTER JOIN tbl_leave_summary" \
                                  " ON tbluser.id = tbl_leave_summary.user_id and tbl_leave_summary.year='" + year + "' " \
                                                                                                                     "where tbluser.\"isActive\"=1 order by tbluser.id desc "

            query.execute(leave_summary_query)
            leave_summary_records = query.fetchall()

            for user in leave_summary_records:

                user_id = user['id']
                user_name = user['rkp_name'] if user['rkp_name'] != None and user['rkp_name'] != "" else user['first_name'] + ("" if user['last_name'] == None else user['last_name'])
                start_of_employment = "" if (user['employment_date'] == '' or user['employment_date'] == None) else user['employment_date'].strftime('%d-%m-%Y')
                previous_year_balance = 0 if user['previous_year_balance'] == None else user['previous_year_balance']
                leave_allocated = 0 if user['leave_allocated'] == None else user['leave_allocated']
                annual_leave = 0 if user['annual_leave'] == None else user['annual_leave']
                leave_taken = 0 if user['leave_taken'] == None else user['leave_taken']
                balance_leave = (user['annual_leave'] - user['leave_taken']) if user['annual_leave'] != None and user['leave_taken'] != None else 0
                leave_others = 0 if user['leave_others'] == None else user['leave_others']
                medical_leave_allocated = 0 if user['medical_leave_allocated'] == None else user['medical_leave_allocated']
                medical_leave = 0 if user['medical_leave'] == None else user['medical_leave']
                balance_medical_leave =  (user['medical_leave_allocated'] - user['medical_leave']) if (user['medical_leave_allocated'] != None and user['medical_leave'] != None) else 0


                serial_no = serial_no + 1

                worksheet.write_number(row, column, serial_no, cell_format)
                worksheet.write_string(row, column + 1, user_name, cell_format)
                worksheet.write_string(row, column + 2, start_of_employment, cell_format)
                worksheet.write_number(row, column + 3, medical_leave_allocated,cell_format)
                worksheet.write_number(row, column + 4, medical_leave,cell_format)
                worksheet.write_number(row, column + 5, balance_medical_leave,cell_format)
                worksheet.write_number(row, column + 6, previous_year_balance, cell_format)
                worksheet.write_number(row, column + 7, leave_allocated, cell_format)
                worksheet.write_number(row, column + 8, annual_leave,cell_format)
                worksheet.write_number(row, column + 9, leave_taken, cell_format)
                worksheet.write_number(row, column + 10, balance_leave, cell_format)
                worksheet.write_number(row, column + 11, leave_others, cell_format)

                column_index = 11

                leave_applied_query = "SELECT * FROM tbl_leave_application  WHERE " \
                                    "EXTRACT(month FROM tbl_leave_application.from_date) = "+month+" AND " \
                                    "EXTRACT(year FROM tbl_leave_application.from_date) = "+year+"  AND " \
                                    "EXTRACT(month FROM tbl_leave_application.to_date) = "+month+"  AND " \
                                    "EXTRACT(year FROM tbl_leave_application.to_date) = "+year+"  AND " \
                                    "tbl_leave_application.user_id = "+str(user_id)+"  AND " \
                                    "tbl_leave_application.status = 3 AND tbl_leave_application.\"isActive\" =1"

                query.execute(leave_applied_query)
                leave_applied_records = query.fetchall()


                for day in dates:
                    day = datetime.strptime(day, "%d-%m-%Y")
                    column_index = column_index + 1
                    for leave in leave_applied_records:
                        from_date = leave['from_date']
                        to_date = leave['to_date']
                        type_of_leave = leave['leave_type'] if (leave['leave_type'] != "" and leave['leave_type'] != None) else ""
                        if (type_of_leave!= "" and len(type_of_leave) <= 2):
                            leave_type = leave_type_data[leave['leave_type']] if (leave['leave_type'] != "" and leave['leave_type'] != None) else ""
                        else:
                            leave_type = type_of_leave

                        if from_date <= day <= to_date:
                            worksheet.write_string(row, column + column_index, leave_type, cell_format)

                row = row + 1

            sum_cell_format = workbook.add_format({'bold': True})
            sum_cell_format.set_align('right')

            updateStatus(connection, 2, pid, filename)

            workbook.close()
            query.close()

        except Exception as e:
             print(e)
             updateStatus(connection, -2, pid, '')
             print('Handling run-time error:')
             logging.error("Exception :", exc_info=True)

        finally:
            if connection is not None:
                connection.close()

    except Exception as e:
        print(e)
        print('Handling run-time error:')
        logging.error("Exception :", exc_info=True)




if __name__ == "__main__":
   main(sys.argv[1:])


