# -*- coding: utf-8 -*-
# Name: service.py
# Description: To generate Workshop Expense Report
# Author: Mycura
# Created: 2020.12.30
# Copyright: © 2020 . All Rights Reserved.
# Change History:
#                |2020.12.30
import calendar
import logging
import socket
from datetime import datetime

import psycopg2
import xlrd
from pandas import *
from ems_config import pg_username, pg_password, pg_host, pg_port, pg_database
import sys
import click
from xlrd.timemachine import xrange

logging.basicConfig(
    handlers=[logging.FileHandler('boss_report.log', 'w', 'utf-8')],
    format='%(levelname)s: %(message)s',
    datefmt='%m-%d %H:%M',
    level=logging.INFO  # CRITICAL ERROR WARNING  INFO    DEBUG    NOTSET
)
number_empty = ['nil', 'nan', '', 'null']


def main():
    try:
        print(" SOCKET CONNECTION STARTS ")
        # Create a socket (SOCK_STREAM means a TCP socket)
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server and send data
        # sock.bind((HOST, PORT))
        # process_file('connection', 'c_date', 'user_id', 'full_path')
        generate_workshop_expense_report()
    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)
    finally:
        print(" CONNECTION CLOSED ")
        # sock.close()


def is_number(s):
    """ Returns True is string is a number. """
    return s.replace('.', '', 1).isdigit()


def process_file(connection, c_date, user_id, full_path):
    try:
        # full_path = 'C:\\Users\\Thiru_office\\Documents\\EMS_malaka\\EXPENSES CAR CARRIER (REPAIR IN MAMBAU).xlsx'
        df = pandas.read_excel(full_path,
                               index_col=None,
                               skiprows=2,
                               sheet_name=0)
        is_new_added, is_retread_added = 0, 0
        header_col_index = {}
        for index, row in df.iterrows():
            is_header = 0
            rt_regn = ''
            remarks = ''
            repair_cost, new_tyre, recamic_tyre, battery, lube, spare_battery_lube, total_from_irs = 0, 0, 0, 0, 0, 0, 0
            for col_index, c_item in enumerate(row.tolist()):
                c_item = str(c_item).strip().lower()
                c_item = '' if c_item == 'nan' else c_item
                if c_item == 'no rt' or c_item == 'lorry no.' or is_header == 1:
                    is_header = 1
                    header_col_index[str(col_index)] = \
                        str(df._get_value(index, col_index, takeable=True)).strip().lower()
                else:
                    if bool(header_col_index):
                        if c_item and str(col_index) in header_col_index:
                            if c_item == 'new' and is_new_added == 0:
                                header_col_index[str(col_index)] = 'new'
                                is_new_added = 1
                            elif c_item == 'retread' and is_retread_added == 0:
                                header_col_index[str(col_index)] = 'retread'
                                is_retread_added = 1
                            elif header_col_index[str(col_index)] == 'lorry no.' or \
                                    header_col_index[str(col_index)] == 'no rt':
                                rt_regn = c_item
                            elif header_col_index[str(col_index)] == 'repair cost':
                                repair_cost = c_item
                            elif header_col_index[str(col_index)] == 'new':
                                new_tyre = c_item
                            elif header_col_index[str(col_index)] == 'retread':
                                recamic_tyre = c_item
                            elif header_col_index[str(col_index)] == 'battery':
                                battery = c_item
                            elif header_col_index[str(col_index)] == 'lubricants':
                                lube = c_item
                            elif 'sparepart' in header_col_index[str(col_index)] and \
                                    'battery' in header_col_index[str(col_index)] and \
                                    'lubricants' in header_col_index[str(col_index)]:
                                spare_battery_lube = c_item
                            elif 'grand total' in header_col_index[str(col_index)]:
                                total_from_irs = c_item
                            elif 'remarks' in header_col_index[str(col_index)]:
                                remarks = c_item
            if rt_regn:
                save_details_to_db(connection, c_date, user_id, rt_regn, repair_cost, new_tyre, recamic_tyre, battery,
                                   lube, spare_battery_lube, total_from_irs, remarks)

    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)


#
#
#
def generate_workshop_expense_report():
    try:
        # Logic
        # 1. Get the list of pending
        # 2 do until remaining
        # 3. process
        # 4. check remaining
        connection = psycopg2.connect(user=pg_username,
                                      password=pg_password,
                                      host=pg_host,
                                      port=pg_port,
                                      database=pg_database)

        try:
            connection.autocommit = True
            print("Connection success - Job Started...")
            logging.error("job started")
            query = connection.cursor()
            pending_query = """
            SELECT report_id, report_date, created_by, full_path	FROM public."tblReportTracker" 
            WHERE status=0 AND report_type=4 AND "isActive"=1; 
            """
            query.execute(pending_query)
            pending_data = query.fetchall()
            for item in pending_data:
                c_date = item[1]
                user_id = item[2]
                report_id = item[0]
                full_path = item[3]
                logging.error("picked report : {report_id}".format(report_id=report_id))
                update_report_status(connection, report_id, 1)
                process_file(connection, c_date, user_id, full_path)
                update_report_status(connection, report_id, 4)
            connection.commit()
            query.close()
            print("Job Completed")
        except Exception as e:
            logging.error(e)
            print("Generate Workshop parts Error : " + str(e))
        connection.close()

    except Exception as e:
        logging.error(e)
        print("Generate Workshop parts Error : " + str(e))


def save_details_to_db(connection, c_date, user_id, rt_regn, repair_cost, new_tyre, recamic_tyre, battery,
                       lube, spare_battery_lube, total_from_irs, remarks):
    try:

        query = connection.cursor()

        report_insert_query = """
                INSERT INTO "tblReportExpense" ( report_date,rt_regn,repair_cost,new_tyre,
                recamic_tyre,battery, lube, spare_battery_lube,total_from_irs,remarks,
                 created_by, created_date, "isActive" ) VALUES 
                                      ( '{report_date}','{rt_regn}',{repair_cost},'{new_tyre}',
                                      {recamic_tyre}, {battery}, {lube}, {spare_battery_lube},{total_from_irs}, 
                                      '{remarks}',
                                      {user_id},'{created_date}',1)
                """
        report_insert_query = report_insert_query.format(report_date=c_date,
                                                         rt_regn=rt_regn,
                                                         repair_cost=repair_cost,
                                                         new_tyre=new_tyre,
                                                         recamic_tyre=recamic_tyre,
                                                         battery=battery,
                                                         lube=lube,
                                                         spare_battery_lube=spare_battery_lube,
                                                         total_from_irs=total_from_irs,
                                                         remarks=remarks,
                                                         user_id=1,
                                                         created_date=datetime.utcnow())

        query.execute(report_insert_query)
        query.close()
    except Exception as e:
        logging.error(e)
        print("Save details Error :" + str(e))


def update_report_status(connection, report_id, status):
    try:
        query = connection.cursor()
        update_report_query = """UPDATE public."tblReportTracker" SET status={status}, updated_date='{updated_date}',
         updated_by=1 WHERE report_id={report_id};
        """
        update_report_query = update_report_query.format(updated_date=datetime.utcnow(),
                                                         status=status,
                                                         report_id=report_id)
        query.execute(update_report_query)
        query.close()
        return 1
    except Exception as e:
        logging.error(e)
        print("Update Status Error : " + str(e))


def remove_null(c_item):
    return '0' if c_item in number_empty else c_item


if __name__ == "__main__":
    main()
