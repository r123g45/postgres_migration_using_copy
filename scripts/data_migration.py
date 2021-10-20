import psycopg2
import threading
import subprocess
import sys
import time
import os

SRC_HOST = sys.argv[1]
WORKING_DIR = sys.argv[2]
start_time = time.perf_counter() # Strting of the processing

SRC_DB_HOST,SRC_DB_NAME, SRC_DB_USERNAME,SRC_DB_PASSWORD = '', '', '', ''
DEST_DB_HOST,DEST_DB_NAME, DEST_DB_USERNAME,DEST_DB_PASSWORD = '', '', '', ''

fileopen = open(''+WORKING_DIR+'/pgpass.txt', 'r')
for dt in fileopen.readlines():
    data = dt.split(" ")
    if SRC_HOST == data[0].strip():
        SRC_DB_HOST = data[0].strip()
        SRC_DB_NAME = data[1].strip()
        SRC_DB_USERNAME = data[2].strip()
        SRC_DB_PASSWORD = data[3].strip()
    else:
        DEST_DB_HOST = data[0].strip()
        DEST_DB_NAME = data[1].strip()
        DEST_DB_USERNAME = data[2].strip()
        DEST_DB_PASSWORD = data[3].strip()
    

SRC_CON_STRING = "-h " + SRC_DB_HOST + " -d " + SRC_DB_NAME + " -U " + SRC_DB_USERNAME + ""
DEST_CON_STRING = "-h " + DEST_DB_HOST + " -d " + DEST_DB_NAME + " -U " + DEST_DB_USERNAME + ""

conn = psycopg2.connect(host='' + SRC_DB_HOST + '', database='' + SRC_DB_NAME + '', user='' + SRC_DB_USERNAME + '', password='' + SRC_DB_PASSWORD + '')
cur = conn.cursor()

f = open(''+WORKING_DIR+'/tables.txt', 'r+')
for table_data in f.readlines():
    table = table_data.split(" ")
    table_name  = table[0].strip() 
    table_schema = table[1].strip()
    table_owner = table[2].strip()
    try:
        QUERY_STRING = "select count(*) from " + table_schema + "." + table_name + ";"
        TRUNCATE_TABLE = "truncate table " + table_schema + "." + table_name + ";"
        DISABE_TRIGGERS = "ALTER TABLE  " + table_schema + "." + table_name + " DISABLE TRIGGER ALL;"
        ENABLE_TRIGGERS = "ALTER TABLE  " + table_schema + "." + table_name + " ENABLE TRIGGER ALL;"

        cur.execute(QUERY_STRING)
        for data in cur.fetchall():
            if int(data[0]) > 0:
                TOTAL_NO_OF_RECORD = data[0]
                conn1 = psycopg2.connect(host='' + DEST_DB_HOST + '', database='' + DEST_DB_NAME + '', user='' + DEST_DB_USERNAME + '', password='' + DEST_DB_PASSWORD + '')
                curr= conn1.cursor()
                curr.execute(QUERY_STRING)
                for dataa in curr.fetchall():
                    if int(dataa[0]) == int(data[0]):
                        print("Data in " + table_schema +"." + table_name +" already present. moving to next table.")
                    else:
                        curr1 = conn1.cursor()
                        curr1.execute(TRUNCATE_TABLE)
                        curr1.close()
                        curr2 = conn1.cursor()
                        curr2.execute(DISABE_TRIGGERS)
                        curr2.close()
                        print("Copying records of table " + table_schema +"." + table_name + ".")
                        select_query = '\"\COPY (SELECT * from ' + table_schema + '.' + table_name + ') TO STDOUT\"'
                        read_query = "PGPASSWORD='" + SRC_DB_PASSWORD + "' psql " + SRC_CON_STRING + " -c " + select_query
                        write_query = "PGPASSWORD='" + DEST_DB_PASSWORD + "' psql " + DEST_CON_STRING + " -c \"\COPY " + table_schema + "." + table_name + " FROM STDIN\""
                        print(read_query + '|' + write_query)
                        os.system(read_query + '|' + write_query)
                        curr3 = conn1.cursor()
                        curr3.execute(ENABLE_TRIGGERS)
                        curr3.close()
                        curr.execute(QUERY_STRING)
                        TOTAL_RECORDS_PROCESSED = 0
                        for i in curr.fetchall():
                            TOTAL_RECORDS_PROCESSED = i[0]
                        print("(" +str(TOTAL_RECORDS_PROCESSED) +") of (" + str(TOTAL_NO_OF_RECORD) + ") records from table " + table_schema +"." + table_name + " processed successfully.")

            else:
                print("No records to update in table " + table_schema +"." + table_name + ".")

    except Exception as table_err:
        print("Error migration : " + table_schema +"."  + table_name + ". Error: {}".format(table_err))

finish_time = time.perf_counter()
print(f'Total time to Migrate the data is:  {round(finish_time-start_time , 2)} Seconds.')







