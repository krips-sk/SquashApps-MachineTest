
from datetime import datetime,timedelta,time

import xlsxwriter
import psycopg2
from psycopg2.extras import RealDictCursor
import os.path
from os import path
import uuid
import config
import sys
import logging

logging.basicConfig(filename='work_summary_report.log', format='%(name)s - %(levelname)s - %(message)s')

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

            select_query_string = "select * from tbl_report_downloads where public_id='" + str(pid) + "' and \"isActive\" =1"
            query.execute(select_query_string)
            report_details = query.fetchall()


            year = report_details[0]['year']
            month = report_details[0]['month']

            updateStatus(connection,1,pid,'')


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
            worksheet.write(row,column+3, 'ACCUMULATED WORKING HRS (A)', header_cell_format)
            worksheet.write(row,column+4, 'CURRENT MONTH WORKING HRS (B)', header_cell_format)
            worksheet.write(row,column+5, 'TOTAL WORKHOURS (A+B)', header_cell_format)

            column_index = 5

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
            user_list_query = "SELECT * FROM tbluser where tbluser.\"isActive\"=1 order by tbluser.id desc "

            query.execute(user_list_query)
            user_list_records = query.fetchall()

            for user in user_list_records:

                user_id = user['id']
                user_name = user['rkp_name'] if user['rkp_name'] != None and user['rkp_name'] != "" else user['first_name'] + ("" if user['last_name'] == None else user['last_name'])
                start_of_employment = "" if (user['employment_date'] == '' or user['employment_date'] == None) else user['employment_date'].strftime('%d-%m-%Y')

                accumalated_work_hrs= ""


                serial_no = serial_no + 1

                worksheet.write_number(row, column, serial_no, cell_format)
                worksheet.write_string(row, column + 1, user_name, cell_format)
                worksheet.write_string(row, column + 2, start_of_employment, cell_format)
                worksheet.write_string(row, column + 3, accumalated_work_hrs, cell_format)


                column_index = 5

                worh_hrs_query = "SELECT * FROM  public.\"tblRKP_login\"   WHERE " \
                                    "EXTRACT(month FROM start_date) = "+month+" AND " \
                                    "EXTRACT(year FROM start_date) = "+year+"  AND " \
                                    "EXTRACT(month FROM stoped_date) = "+month+"  AND " \
                                    "EXTRACT(year FROM stoped_date) = "+year+"  AND " \
                                    "user_id = "+str(user_id)+"  AND " \
                                    "rt_status = 2 AND \"isActive\" =1"

                query.execute(worh_hrs_query)
                worh_hrs_records = query.fetchall()
                current_month_work_hrs = 0

                for day in dates:

                    day = datetime.strptime(day, "%d-%m-%Y")

                    last_hrs = datetime.combine(day, time.max)
                    first_hrs = datetime.combine(day, time.min)

                    column_index = column_index + 1
                    for work in worh_hrs_records:

                        start_date = work['start_date']
                        stoped_date = work['stoped_date']

                        mins_data = 0

                        if start_date <= day <= stoped_date:

                            if start_date.date() <= day.date() <= stoped_date.date():

                                if start_date.date() == day.date() and stoped_date.date() == day.date():
                                    difference_date = stoped_date - start_date
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_data = mins[0]

                                elif start_date.date() == day.date() and stoped_date.date() != day.date():
                                    difference_date = last_hrs - start_date
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_data = mins[0]

                                elif start_date.date() != day.date() and stoped_date.date() == day.date():
                                    difference_date = stoped_date - first_hrs
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_data = mins[0]

                                else:
                                    mins = 1440
                                    mins_data = mins


                            #mins to hrs
                            if mins_data != 0:
                                hrs_data = "{}:{}".format(*divmod(int(mins_data), 60))
                                worksheet.write_string(row, column + column_index, hrs_data, cell_format)

                        current_month_work_hrs = current_month_work_hrs + mins_data

                month_total_hrs = "{}:{}".format(*divmod(int(current_month_work_hrs), 60))
                total_hrs = month_total_hrs
                worksheet.write_string(row, column + 4, month_total_hrs, cell_format)
                worksheet.write_string(row, column + 5, total_hrs, cell_format)
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


