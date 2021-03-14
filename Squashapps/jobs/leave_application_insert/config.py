import os.path

postgresusername="appuser";
postgrespassword="vgy7*uhb";
host="103.138.188.53";
port="5432";
database="ems_stg";

log_path = os.path.abspath(os.path.dirname("../../jobs/leave_application_insert/log/"))
input_file_path = os.path.abspath(os.path.dirname("../../jobs/leave_application_insert/"))
file_name = 'LEAVERKPMEDICAL.xlsx'
leave_type = 2