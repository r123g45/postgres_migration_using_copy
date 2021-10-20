from multiprocessing.context import Process
import psycopg2
import threading
import subprocess
import sys
import os
import concurrent.futures
import time
from multiprocessing import process

start_time = time.perf_counter() # Strting of the processing

SRC_HOST = sys.argv[1]
WORKING_DIR = sys.argv[2]
CPU_COUNT = os.cpu_count()

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

print(f'Cpu cores of the machine is : {CPU_COUNT}') 

def data_Migration(dict_of_table):
    for key in dict_of_table.keys():
            if key == "table_schema":
                table_schema = dict_of_table[key]
            elif key == "table_name":
                table_name = dict_of_table[key] 

    try:
        QUERY_STRING = "select count(*) from " + table_schema + "." + table_name + ";"
        TRUNCATE_TABLE = "truncate table " + table_schema + "." + table_name + ";"

        conn = psycopg2.connect(host=SRC_DB_HOST, database=SRC_DB_NAME, user=SRC_DB_USERNAME, password=SRC_DB_PASSWORD)
        cur = conn.cursor()
        cur.execute(QUERY_STRING)
        for data in cur.fetchall():
            if int(data[0]) > 0:
                TOTAL_NO_OF_RECORD = data[0]
                conn1 = psycopg2.connect(host=DEST_DB_HOST, database=DEST_DB_NAME, user=DEST_DB_USERNAME, password=DEST_DB_PASSWORD)
                curr= conn1.cursor()
                curr.execute(QUERY_STRING)
                for dataa in curr.fetchall():
                    if int(dataa[0]) == int(data[0]):
                        print("Data in " + table_schema +"." + table_name +" already present moving to next table.")
                        pass
                    else:
                        #curr.execute(TRUNCATE_TABLE)
                        print("Copying records of table " + table_schema +"." + table_name + "." )
                        select_query = '\"\COPY (SELECT * from ' + table_schema + '.' + table_name + ' ) TO STDOUT\"'
                        read_query = "PGPASSWORD='" + SRC_DB_PASSWORD + "' psql " + SRC_CON_STRING + " -c " + select_query
                        write_query = "PGPASSWORD='" + DEST_DB_PASSWORD + "' psql " + DEST_CON_STRING + " -c \"\COPY " + table_schema + "." + table_name + " FROM STDIN\""
                        #print(read_query + '|' + write_query)
                        os.system(read_query + '|' + write_query)
                        TOTAL_RECORDS_PROCESSED = 0
                        curr.execute(QUERY_STRING)
                        for i in curr.fetchall():
                            TOTAL_RECORDS_PROCESSED = i[0]
                        print("(" +str(TOTAL_RECORDS_PROCESSED) +") of (" + str(TOTAL_NO_OF_RECORD) + ") records from table " + table_schema +"." + table_name + " processed successfully.")
               
            else:
                print("No records to update in table " + table_name + ".")

    except Exception as table_err:
        print("No records in table " + table_name + ". Error: {}".format(table_err))

# getting  higest dependency level from the Tables.txt to iterate loop on dependency level
for line in reversed(list(open(""+WORKING_DIR+"/tables.txt"))):
    line = line.strip()
    _ , _,range_to_iterate_loop = line.split(" ")
    break
print("Number of dependency present in DB: " + range_to_iterate_loop)

for loop_value in range(1, int(range_to_iterate_loop) + 1):

    list_of_tables = []
    processes = []

    f = open(''+WORKING_DIR+'/tables.txt', 'r+')
    for table_data in f.readlines():
        table = table_data.split(" ")
        tablename  = table[0].strip() 
        tableschema = table[1].strip()
        dependency_level = table[2].strip()

        if str(loop_value) == dependency_level:
            # defining dictionary to input in list
            data_table_name = {}
            data_table_name["table_schema"] = tableschema
            data_table_name["table_name"] = tablename
            data_table_name["label"] = dependency_level
            list_of_tables.append(data_table_name)
    
    print(f'list of tables with their schema name for dependency level " {loop_value} " is as follows : {list_of_tables} \n total_table_to_be_migrated = {len(list_of_tables)}')
    length_of_list = len(list_of_tables)
    
    '''for length in range(length_of_list):
        process_name = f'p{length}'
        process_name = Process(target=data_Migration, args=(list_of_tables[length],))
        processes.append(process_name)
        process_name.start()

    for process in processes:
        process.join()'''

    with concurrent.futures.ProcessPoolExecutor() as executer:
        executer.map(data_Migration, list_of_tables) # calling data_migration function
    
    list_of_tables.clear()
    processes.clear()


finish_time = time.perf_counter()
print(f'Total time to Migrate the data is:  {round(finish_time-start_time , 2)} Seconds.')