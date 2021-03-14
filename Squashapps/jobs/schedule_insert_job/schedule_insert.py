import csv
from datetime import datetime
import re
import shutil
import uuid
import pandas
import psycopg2
import os.path
from os import path
import config
import requests
import os
import logging
import xlrd
from psycopg2.extras import RealDictCursor

postgers_connection = psycopg2.connect(user=config.postgresusername,
                                        password=config.postgrespassword,
                                        host=config.host,
                                        port=config.port,
                                        database=config.database)


def insert_into_table(data_list):
    try:

        if data_list:

            user_name = data_list[0]['user_name']
            user_name = user_name.replace("'", "").strip()
            query = postgers_connection.cursor(cursor_factory=RealDictCursor)

            user_query = "select * from public.tbluser where first_name = '" + str(user_name) +"' and \"isActive\" = 1 "
            query.execute(user_query)
            user = query.fetchall()

            if user:
                user_id = user[0]['id']

                for data in data_list:

                    sche_category = data['sche_category']
                    rt_rgno = data['rt_rgno']
                    sche_date = data['date_time']
                    sche_type = data['sche_type']

                    # count_query = "select count(*) from public.\"tblSchedule\" where  schedule_date = '" + str(sche_date) + "' and rt_regn ='"+str(rt_rgno) +"' and user_id=" + str(user_id)
                    # query.execute(count_query)
                    # data = query.fetchone()
                    # total_count = data['count']

                    total_count = 0

                    if total_count == 0:

                        insert_query = "INSERT INTO  public.\"tblSchedule\" (user_id, rt_regn,schedule_date,schedule_category,schedule_type,created_date, \"isActive\" ) " \
                                       "VALUES (" + str(user_id) + ",'" + str(rt_rgno) + "','" + str(sche_date) + "','" + str(sche_category) + "','" + str(sche_type)  + "', now(), 1)"
                        query.execute(insert_query)
                        postgers_connection.commit()

    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def get_information_from_excel():
    try:
        lst = []
        start_row = 5
        start_row_type = 2

        loc = os.path.abspath(config.input_file_path+'/'+config.file_name)

        # To open Workbook
        wb = xlrd.open_workbook(loc)
        sheet_list = wb.sheet_names()
        print(sheet_list)
        sheet_list = ['NOV 2020']
        # June Completed
        for sheet_name in sheet_list:

            month = sheet_name.split(" ")[0]

            if month == 'MAC':
                month = 'MAR'
            elif month == 'JULAI':
                month = 'JUL'
            elif month == 'OGOS':
                month ='AUG'
            elif month == 'SEPT':
                month ='SEP'


            year = sheet_name.split(" ")[1]
            sheet = wb.sheet_by_name(sheet_name)
            previous_rt = ""
            previous_type = ""
            for row in range(sheet.nrows):
                rt = previous_rt

                if row >= start_row_type:
                    rt_type = sheet.cell(row, 0).value

                    if type(rt_type) is not float and rt_type != '' and rt_type != 'No':
                        previous_type = rt_type
                    else:
                        rt_type = previous_type

                    if 'TOTAL' in rt_type:
                        break

                if row >= start_row:
                    rt = sheet.cell(row, 1).value
                    if rt == '':
                        rt = previous_rt
                    else:
                        previous_rt = rt

                    user_name =sheet.cell(row, 3).value
                    date_column = 1
                    if user_name != '' and user_name != 'RKP' and type(user_name) is not float:
                        lst = []
                        for column in range(sheet.ncols):
                            if column > 3 and column < 35:
                                date_format = str(date_column)+'/'+month+'/'+year
                                sche_type = sheet.cell(row, column).value

                                if sche_type != '':
                                    date_time = datetime.strptime(date_format, "%d/%b/%Y")


                                date_column = date_column + 1

                                if sche_type != '':
                                    data = {}
                                    data['sche_category']=rt_type
                                    data['rt_rgno'] = rt
                                    data['date_time'] = date_time
                                    data['sche_type'] = sche_type
                                    data['user_name'] = user_name

                                    lst.append(data)

                        insert_into_table(lst)

                if 'TOTAL' in previous_type:
                    break

            print("Completed Sheet -- " + sheet_name)


    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def main():
    try:
        get_information_from_excel()
    except Exception as e:
        print("error in main "+str(e))
        logging.error("Exception :", exc_info=True)
    finally:
        postgers_connection.close()
        print("finish")

if __name__ == "__main__":
   main()