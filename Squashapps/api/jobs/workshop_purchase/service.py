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
import re
import socket
import uuid
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
number_empty = ['nil', 'nan', '', 'null', '-']


def main():
    try:
        print(" SOCKET CONNECTION STARTS ")
        # Create a socket (SOCK_STREAM means a TCP socket)
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server and send data
        # sock.bind((HOST, PORT))
        generate_workshop_purchase_report()
    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)
    finally:
        print(" CONNECTION CLOSED ")
        # sock.close()


def is_number(s):
    """ Returns True is string is a number. """
    return s.replace('.', '', 1).isdigit()


def process_file(connection, c_year, user_id, full_path):
    try:
        months = dict((month, index) for index, month in enumerate(calendar.month_abbr) if month)
        # full_path = 'C:\\Users\\Thiru_office\\Documents\\EMS_malaka\\Purchase Report 2020 - New Version.xlsx'
        df = pandas.read_excel(full_path,
                               index_col=None,
                               skiprows=2,
                               sheet_name=0)
        c_month = 0
        header_col_index = {}
        for index, row in df.iterrows():
            is_header = 0
            supplier, payment = '', 0
            for col_index, c_item in enumerate(row.tolist()):
                c_item = str(c_item).strip().lower()
                c_item = '' if c_item == 'nan' else c_item
                if c_item == 'supplier / month' or is_header == 1:
                    is_header = 1
                    header_col_index[str(col_index)] = \
                        str(df._get_value(index, col_index, takeable=True)).strip().lower()
                else:
                    if bool(header_col_index):
                        if c_item and str(col_index) in header_col_index:
                            if header_col_index[str(col_index)] == 'supplier / month':
                                if 'total (month)' in c_item:
                                    return 0
                                supplier = re.sub('\s+', ' ', c_item)
                            else:
                                payment = remove_null(c_item)
                                # here we need to save details to database.
                                # need to find month
                                if header_col_index[str(col_index)][:3].title() in months:
                                    c_month = months[header_col_index[str(col_index)][:3].title()]
                                    if payment != '0':
                                        report_date = c_year + "-" + str(c_month) + "-" + "01"
                                        print(
                                            "Saving details for supplier : " + supplier + ". date: " + str(report_date)
                                            + " Amount : " + str(payment))
                                        save_details_to_db(connection, report_date, supplier, payment)

    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)


#
#
#
def generate_workshop_purchase_report():
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
            SELECT report_id, extract(year from report_date), created_by, full_path	FROM public."tblReportTracker" 
            WHERE status=0 AND report_type=2 AND "isActive"=1; 
            """
            query.execute(pending_query)
            pending_data = query.fetchall()
            for item in pending_data:
                c_year = item[1]
                c_year = str(int(c_year))
                user_id = item[2]
                report_id = item[0]
                full_path = item[3]
                logging.error("picked report : {report_id}".format(report_id=report_id))
                update_report_status(connection, report_id, 1)
                process_file(connection, c_year, user_id, full_path)
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


def get_exists_supplier(connection, supplier):
    try:
        supplier_id = 0
        query = connection.cursor()
        exists_query = """ SELECT id FROM "tblSupplier" WHERE "isactive"=1 AND supplier_name ilike '{supplier}' ; 
                        """
        exists_query = exists_query.format(supplier=supplier)
        query.execute(exists_query)
        exists_data = query.fetchone()
        if exists_data:
            supplier_id = exists_data[0]
        query.close()
        return supplier_id
    except Exception as e:
        logging.error(e)
        print("Generate Workshop parts Error : " + str(e))
        return 0


def get_supplier_id(connection, supplier):
    try:
        supplier_id = get_exists_supplier(connection, supplier)
        if supplier_id > 0:
            return supplier_id
        else:
            public_id = str(uuid.uuid4())

            query = connection.cursor()
            report_insert_query = """
                            INSERT INTO "tblSupplier" ( public_id, supplier_name,
                             created_by, created_date, "isactive" ) VALUES 
                                                  ( '{public_id}','{supplier}',
                                                  {user_id},'{created_date}',1)
                            """
            report_insert_query = report_insert_query.format(public_id=public_id,
                                                             supplier=supplier,
                                                             user_id=1,
                                                             created_date=datetime.utcnow())

            query.execute(report_insert_query)
            query.close()
            supplier_id = get_exists_supplier(connection, supplier)
            return supplier_id
    except Exception as e:
        logging.error(e)
        print("Generate Workshop parts Error : " + str(e))


def save_details_to_db(connection, report_date, supplier, payment):
    try:
        supplier_id = get_supplier_id(connection, supplier)
        query = connection.cursor()
        exists_query = """ SELECT 1 FROM "tblReportWorkshopPurchase" WHERE "isActive"=1 AND supplier_id={supplier_id} 
        AND report_date='{report_date}'::date; 
        """
        exists_query = exists_query.format(supplier_id=supplier_id, report_date=report_date)
        query.execute(exists_query)
        exists_data = query.fetchall()
        if exists_data:
            # update query
            update_query = """UPDATE public."tblReportWorkshopPurchase" SET payment={payment},
             updated_date='{updated_date}'
                                        WHERE "isActive"=1 AND supplier_id={supplier_id} 
                AND report_date='{report_date}'::date; """
            update_query = update_query.format(supplier_id=supplier_id,
                                               report_date=report_date,
                                               payment=payment,
                                               updated_date=datetime.utcnow())
            query.execute(update_query)
        else:
            report_insert_query = """
                    INSERT INTO "tblReportWorkshopPurchase" ( payment,supplier_id,report_date,
                     created_by, created_date, "isActive" ) VALUES 
                                          ( {payment},{supplier_id},'{report_date}',
                                          {user_id},'{created_date}',1)
                    """
            report_insert_query = report_insert_query.format(supplier_id=supplier_id,
                                                             report_date=report_date,
                                                             payment=payment,
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
