# -*- coding: utf-8 -*-
# Name: service.py
# Description: To generate workshop parts Report
# Author: Mycura
# Created: 2020.10.13
# Copyright: © 2020 . All Rights Reserved.
# Change History:
#                |2020.10.13
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
    handlers=[logging.FileHandler('workshop_parts.log', 'w', 'utf-8')],
    format='%(asctime)s - [%(filename)s:%(lineno)d] - %(funcName)20s() %(message)s',
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
        generate_workshop_parts_report()
    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)
    finally:
        print(" CONNECTION CLOSED ")
        # sock.close()


def get_summary_start_pos(full_path):
    cost_summary_list = []
    branch_summary_list = []
    try:

        df = pandas.read_excel(full_path,
                               index_col=None,
                               skiprows=20,
                               sheet_name='2020').fillna(method='ffill', axis=1)
        for row in range(df.shape[0]):  # df is the DataFrame
            for col in range(df.shape[1]):
                if str(df._get_value(row, col, takeable=True)).strip().lower() == 'total cost (rm)':
                    cost_summary_list.append({
                        "row": row,
                        "col": col
                    })
                elif str(df._get_value(row, col, takeable=True)).strip().lower() == 'total cost from branches(rm)':
                    branch_summary_list.append({
                        "row": row,
                        "col": col
                    })

    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)
    return cost_summary_list, branch_summary_list


def get_start_pos(full_path, c_year):
    final_row, final_col = 0, 0
    try:

        df = pandas.read_excel(full_path,
                               index_col=None,
                               nrows=20,
                               sheet_name=c_year).fillna(method='ffill', axis=1)
        for row in range(df.shape[0]):  # df is the DataFrame
            for col in range(df.shape[1]):
                if str(df._get_value(row, col, takeable=True)).strip().lower() == 'month/ branches':
                    print(row, col)
                    final_row, final_col = row, col
                    return final_row, final_col

    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)
    return final_row, final_col


def is_number(s):
    """ Returns True is string is a number. """
    return s.replace('.', '', 1).isdigit()


def process_summary(connection, c_year, full_path):
    try:
        tc_branch_col_index = {}
        tcf_branch_col_index = {}
        # cost_summary_list, branch_summary_list = get_summary_start_pos(full_path)
        df = pandas.read_excel(full_path,
                               index_col=None,
                               skiprows=12,
                               sheet_name=c_year).fillna(method='ffill', axis=1)
        current_description, current_amount, branch_type, branch_name = '', 0, 1, ''
        for index, row in df.iterrows():
            for col_index, c_item in enumerate(row.tolist()):
                c_item = str(c_item).strip().lower()
                if c_item == 'total cost (rm)':
                    tc_branch_col_index[str(col_index)] = \
                        str(df._get_value(index - 1, col_index, takeable=True)).strip().lower()
                elif c_item == 'total cost from branches(rm)' or c_item == 'total cost from':
                    tcf_branch_col_index[str(col_index)] = \
                        str(df._get_value(index - 1, col_index, takeable=True)).strip().lower()
                else:
                    if bool(tcf_branch_col_index):
                        if c_item:
                            if is_number(c_item):
                                current_amount = float(c_item)
                            else:
                                current_description = c_item
                                current_amount = 0
                            if str(col_index) in tc_branch_col_index:
                                branch_type = 1
                                branch_name = tc_branch_col_index[str(col_index)]
                            elif str(col_index) in tcf_branch_col_index:
                                branch_type = 2
                                branch_name = tcf_branch_col_index[str(col_index)]
                            if current_amount > 0:
                                # need to save
                                print(current_amount)
                                if current_description and branch_name and 'grand total' not in current_description\
                                        and current_description != 'nan':
                                    save_summary(connection, c_year, current_description, current_amount,
                                                 branch_type, branch_name)
                                    current_description, current_amount, branch_type, branch_name = '', 0, 1, ''

    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)


def process_file(connection, c_year, user_id, full_path):
    try:
        months = dict((month, index) for index, month in enumerate(calendar.month_abbr) if month)
        # full_path = 'C:\\Users\\Thiru_office\\Documents\\EMS_malaka\\Parts Delivered to Respective Branches.xlsx'
        final_row, final_col = get_start_pos(full_path, c_year)
        df = pandas.read_excel(full_path,
                               index_col=None,
                               skiprows=final_row,
                               nrows=13,
                               sheet_name=c_year,
                               usecols=range(final_col, 20)).fillna(method='ffill', axis=1)
        branches = []
        headers = []
        c_month = 0
        payment_delivery = 0
        payment_sale = 0
        is_sale_added = 0
        for index, row in df.iterrows():
            for col_index, c_item in enumerate(row.tolist()):
                c_item = str(c_item).strip().lower()
                if index == 0:
                    branches.append(c_item)
                elif index == 1:
                    headers.append(c_item)
                else:
                    if col_index == 0:
                        c_month = months[c_item[:3].title()]
                        print(c_item)  # this is month details
                    else:
                        if headers[col_index] == 'delivered':
                            payment_delivery = remove_null(c_item)
                            is_sale_added = 0
                        elif headers[col_index] == "sale" and is_sale_added == 0:
                            payment_sale = remove_null(c_item)
                            branch_name = branches[col_index]
                            save_details_to_db(connection, c_month, payment_delivery, payment_sale, branch_name, c_year)
                            is_sale_added = 1
                            # here we need to save the collected items.
        process_summary(connection, c_year, full_path)

        """
        wb = xlrd.open_workbook(full_path)
        sheet_list = wb.sheet_names()
        for sheet_name in sheet_list:
            sheet = wb.sheet_by_name(sheet_name)
            for crange in sheet.merged_cells:
                rlo, rhi, clo, chi = crange
                for rowx in xrange(rlo, rhi):
                    for colx in xrange(clo, chi):
                        print(colx)

            for row in range(sheet.nrows):
                for column in range(sheet.ncols):
                    column_name = sheet.cell(row, column).value
                    if column_name == 'MONTH/ BRANCHES ':
                        print(column_name)
        """
    except Exception as e:
        print("Main Error" + str(e))
        logging.error(e)


#
#
#
def generate_workshop_parts_report():
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
            WHERE status=0 AND report_type=1 AND "isActive"=1; 
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


def get_branch_id(connection, branch_name):
    try:
        # need to get the transaction withdrawal
        branch_query = """
                select 
                id

                from "tblbranch" bt where bt."isactive"=1 
                AND  bt.branch_name  ilike '{branch_name}%' 
                """
        query = connection.cursor()
        branch_query = branch_query.format(branch_name=branch_name)
        query.execute(branch_query)
        branch_data = query.fetchone()
        branch_id = branch_data[0]
        return branch_id
    except Exception as e:
        logging.error(e)
        print("Getting branch Error :" + str(e))


def save_summary(connection, c_year, current_description, current_amount, branch_type, branch_name):
    try:
        branch_id = get_branch_id(connection, branch_name)
        report_date = c_year + "-01-01"
        query = connection.cursor()
        exists_query = """ SELECT 1 FROM public."tblReportBranchPartsSummary" WHERE "isActive"=1 AND branch_id={branch_id} 
        AND report_date='{report_date}'::date AND branch_type={branch_type} and description='{description}'; 
        """
        exists_query = exists_query.format(branch_id=branch_id, report_date=report_date,
                                           branch_type=branch_type,
                                           description=current_description)
        query.execute(exists_query)
        exists_data = query.fetchall()
        if exists_data:
            # update query
            update_query = """UPDATE public."tblReportBranchPartsSummary" SET description='{description}',
            payment={payment}, updated_date='{updated_date}'
                                        WHERE "isActive"=1 AND branch_id={branch_id} 
                AND report_date='{report_date}'::date AND branch_type={branch_type} AND description='{description}'; """
            update_query = update_query.format(branch_id=branch_id,
                                               report_date=report_date,
                                               description=current_description,
                                               payment=current_amount,
                                               branch_type=branch_type,
                                               updated_date=datetime.utcnow())
            query.execute(update_query)
        else:
            report_insert_query = """
                    INSERT INTO "tblReportBranchPartsSummary" ( branch_type,payment,description,branch_id,report_date,
                     created_by, created_date, "isActive" ) VALUES 
                                          ( {branch_type},{payment},'{description}',{branch_id},'{report_date}',
                                          {user_id},'{created_date}',1)
                    """
            report_insert_query = report_insert_query.format(branch_id=branch_id,
                                                             report_date=report_date,
                                                             description=current_description,
                                                             payment=current_amount,
                                                             branch_type=branch_type,
                                                             user_id=1,
                                                             created_date=datetime.utcnow())

            query.execute(report_insert_query)
        query.close()
    except Exception as e:
        logging.error(e)
        print("Save details Error :" + str(e))


def save_details_to_db(connection, c_month, payment_delivered, payment_sale, branch_name, c_year):
    try:
        branch_id = get_branch_id(connection, branch_name)
        report_date = c_year + "-" + str(c_month) + "-" + "01"
        if branch_id == 1 and c_month == 1:
            print(branch_id)
        query = connection.cursor()
        exists_query = """ SELECT 1 FROM "tblReportBranchParts" WHERE "isActive"=1 AND branch_id={branch_id} 
        AND report_date='{report_date}'::date; 
        """
        exists_query = exists_query.format(branch_id=branch_id, report_date=report_date)
        query.execute(exists_query)
        exists_data = query.fetchall()
        if exists_data:
            # update query
            update_query = """UPDATE public."tblReportBranchParts" SET payment_delivered={payment_delivered},
            payment_sale={payment_sale}, updated_date='{updated_date}'
                                        WHERE "isActive"=1 AND branch_id={branch_id} 
                AND report_date='{report_date}'::date; """
            update_query = update_query.format(branch_id=branch_id,
                                               report_date=report_date,
                                               payment_delivered=payment_delivered,
                                               payment_sale=payment_sale,
                                               updated_date=datetime.utcnow())
            query.execute(update_query)
        else:
            report_insert_query = """
                    INSERT INTO "tblReportBranchParts" ( payment_delivered,payment_sale,branch_id,report_date,
                     created_by, created_date, "isActive" ) VALUES 
                                          ( {payment_delivered},{payment_sale},{branch_id},'{report_date}',
                                          {user_id},'{created_date}',1)
                    """
            report_insert_query = report_insert_query.format(branch_id=branch_id,
                                                             report_date=report_date,
                                                             payment_delivered=payment_delivered,
                                                             payment_sale=payment_sale,
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
