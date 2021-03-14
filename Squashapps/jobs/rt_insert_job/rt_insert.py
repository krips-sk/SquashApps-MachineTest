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


def insert_into_table(category,vehicle_no,capacity,depoh,remark):
    try:

        if vehicle_no:

            query = postgers_connection.cursor(cursor_factory=RealDictCursor)

            vehicle_query = "select * from public.tbl_vehicle where regn_no = '" + str(vehicle_no) +"' and \"isActive\" = 1 "
            query.execute(vehicle_query)
            vehicle = query.fetchall()

            if vehicle:
                update_query = "UPDATE  public.tbl_vehicle set " \
                               "engine_capacity ='" + str(capacity) +"' , vehicle_category = '"+str(category)+"' ," \
                                " vehicle_remark ='"+str(remark)+"' , vehicle_depoh ='"+str(depoh)+"' " \
                                "where regn_no = '" + str(vehicle_no) +"' and \"isActive\" = 1 "

                query.execute(update_query)
                postgers_connection.commit()

            else:
                public_id = str(uuid.uuid4())
                insert_query = "INSERT INTO  public.tbl_vehicle (public_id,regn_no, engine_capacity,vehicle_category,vehicle_remark,vehicle_depoh,created_date, \"isActive\" ) " \
                               "VALUES ('" + str(public_id) + "','"+ str(vehicle_no) + "','" + str(capacity) + "','" + str(category) + "','" + str(remark) + "','" + str(depoh)  + "', now(), 1)"
                query.execute(insert_query)
                postgers_connection.commit()


    except Exception as e:
        print(e)
        logging.error("Exception :", exc_info=True)


def get_information_from_excel():
    try:
        loc = os.path.abspath(config.input_file_path + '/' + config.file_name)

        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)

        for row in range(sheet.nrows):
            if row != 0:
                category = sheet.cell(row, 0).value
                vehicle_no = sheet.cell(row, 1).value
                capacity = sheet.cell(row, 2).value

                if type(capacity) is float:
                    capacity = int(capacity)

                depoh = sheet.cell(row, 3).value
                remark = sheet.cell(row, 4).value

                insert_into_table(category,vehicle_no,capacity,depoh,remark)



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