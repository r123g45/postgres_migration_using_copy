import psycopg2
import subprocess
import sys
import os
import time

QUERY_STR = """WITH RECURSIVE fkeys AS (
   SELECT conrelid AS source, confrelid AS target
   FROM pg_constraint
   WHERE contype = 'f'
),
tables AS (
      (
          SELECT c.oid AS table_name, 1 AS level, ARRAY[c.oid] AS trail, FALSE AS circular, ns.nspname as schema_name
          FROM pg_class as c
		  JOIN pg_catalog.pg_namespace AS ns
  ON c.relnamespace = ns.oid
          WHERE relkind = 'r'
            AND NOT relnamespace::regnamespace::text LIKE ANY
                    (ARRAY['pg_catalog', 'information_schema', 'pg_temp_%'])
       EXCEPT
          SELECT source, 1, ARRAY[ source ], FALSE, null
          FROM fkeys
      )
   UNION ALL
      SELECT fkeys.source, tables.level + 1, tables.trail || fkeys.source, tables.trail @> ARRAY[fkeys.source], schema_name
      FROM fkeys JOIN tables ON tables.table_name = fkeys.target
      WHERE cardinality(array_positions(tables.trail, fkeys.source)) < 2
),
ordered_tables AS (
   SELECT DISTINCT ON (table_name) table_name, level, circular, schema_name
   FROM tables
   ORDER BY table_name, level DESC
)
SELECT table_name::regclass, level , schema_name
FROM ordered_tables
WHERE NOT circular
ORDER BY level, table_name;"""


SRC_HOST = sys.argv[1]
WORKING_DIR = sys.argv[2]
WORKSPACE_DIR = os.environ['WORKSPACE']
SRC_DB_HOST,SRC_DB_NAME, SRC_DB_USERNAME,SRC_DB_PASSWORD = '', '', '', ''
DEST_DB_HOST,DEST_DB_NAME, DEST_DB_USERNAME,DEST_DB_PASSWORD = '', '', '', ''
value = ''

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

try:
    conn = psycopg2.connect(host='' + SRC_DB_HOST + '', database='' + SRC_DB_NAME + '', user='' + SRC_DB_USERNAME + '', password='' + SRC_DB_PASSWORD + '')
    cur = conn.cursor()
    cur.execute(QUERY_STR)
    f = open(""+WORKING_DIR+"/tables.txt", "w")

    for table in cur.fetchall():
       table_name, table_schema, level = table[0], table[2], table[1]
       if "." in table_name:
           parse_var = str(table_name).split(".")
           table_name = parse_var[1]
       else:
            pass
       value = table_name, " ",  str(table_schema).strip(), " ", str(level).strip(),"\n"
       f.writelines(value)
       
    f.close()
    conn.close()
    print("Table.txt has been updated with the data.")

except Exception as fetch_err:
    print('Error during table data update: {}'.format(fetch_err))

# check if DB is present at destination cluster, if not create the DB.

try:
    con = psycopg2.connect(host='' + DEST_DB_HOST + '', database='postgres', user='' + DEST_DB_USERNAME + '', password='' + DEST_DB_PASSWORD + '')
    if con is not None:
        con.autocommit = True
        curr = con.cursor()
        curr.execute("SELECT datname FROM pg_database;")
        list_database = curr.fetchall()

        if (DEST_DB_NAME,) in list_database:
            print("'{}' Database already exist".format(DEST_DB_NAME))
        else:
            CREATE_DB = "create database " + SRC_DB_NAME + ";"
            curr.execute(CREATE_DB)
            print("Database " + SRC_DB_NAME + " created successfully. Proceeding to Roles and Schema migration.")
    con.close()

except Exception as db_creation_err:
        print('Error during DB creation : {}'.format(db_creation_err))

    
GET_DB_SIZE = "SELECT pg_size_pretty(pg_database_size('"  + SRC_DB_NAME + "'));"
SRC_DB_SIZE = ""
conn1 = psycopg2.connect(host=SRC_DB_HOST, database=SRC_DB_NAME, user=SRC_DB_USERNAME, password=SRC_DB_PASSWORD)
curr1 = conn1.cursor()
curr1.execute(GET_DB_SIZE)
for size in curr1.fetchall():
    SRC_DB_SIZE = str(size[0])
cur.close()
print("Total size of " + SRC_DB_NAME + " is =======>>>>>> " + SRC_DB_SIZE)




