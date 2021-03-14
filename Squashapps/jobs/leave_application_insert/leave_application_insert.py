import csv
import datetime
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

postgers_connection = psycopg2.connect(user=config.postgresusername,
                                        password=config.postgrespassword,
                                        host=config.host,
                                        port=config.port,
                                        database=config.database)


def insert_into_table(user_id,a1_as_datetime):
    try:

        from_date = a1_as_datetime
        to_date = a1_as_datetime
        no_of_days = 1
        leave_type = config.leave_type
        status = 1

        query = postgers_connection.cursor()

        count_query = "select count(*) from public.tbl_leave_application where  from_date = '"+str(from_date)+"' and user_id="+str(user_id)
        query.execute(count_query)
        data = query.fetchone()
        total_count = data[0]

        if total_count == 0:
            insert_query = "INSERT INTO  public.tbl_leave_application (user_id, from_date,to_date,days_of_leave,leave_type,status,created_date, \"isActive\" ) " \
                           "VALUES (" + str(user_id) + ",'" + str(from_date) + "','" + str(to_date) + "'," + str(no_of_days) + "," + str(leave_type) + ", " + str(status) + ", now(), 1)"
            query.execute(insert_query)
            postgers_connection.commit()

    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def get_information_from_excel():
    try:
        loc = os.path.abspath(config.input_file_path+'/'+config.file_name)

        # To open Workbook
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)

        for row in range(sheet.nrows):
            if row != 0:
                user_id = int(sheet.cell(row, 1).value)
                for column in range(sheet.ncols):
                    if column > 1:
                        date = sheet.cell(row, column).value
                        if type(date) is float:
                            a1_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(date, wb.datemode))
                            print(a1_as_datetime)
                            insert_into_table(user_id,a1_as_datetime)

                print(user_id)


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

if __name__ == "__main__":
   main()