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


def insert_into_table(age,status,user_name):
    try:

        if user_name:

            query = postgers_connection.cursor(cursor_factory=RealDictCursor)
            user_name = user_name.replace("'", "").strip()
            user_query = "select * from public.tbluser where first_name = '" + str(user_name) + "' and \"isActive\" = 1 "
            query.execute(user_query)
            user = query.fetchall()

            if user:
                user_id = user[0]['id']

                update_query = "UPDATE  public.tbluser set " \
                               "age =" + str(age) +" , status = '"+str(status)+"' where id = " + str(user_id) +" and \"isActive\" = 1 "

                query.execute(update_query)
                postgers_connection.commit()
            else:
                print("No Valid User")



    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def get_information_from_excel():
    try:
        loc = os.path.abspath(config.input_file_path + '/' + config.file_name)

        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)

        for row in range(sheet.nrows):
            if row > 98:
                age = sheet.cell(row, 4).value
                status = sheet.cell(row, 7).value
                user_name = sheet.cell(row, 2).value

                if type(age) is float:
                    age = int(age)


                insert_into_table(age,status,user_name)



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