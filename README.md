# postgres_migration_using_-copy
This repo contains code which migrate your postgres DB from source to destination using \copy command
make sure your jenkins machine will have access to the source and destination server.

create a jenkins pipeline using the jenkinsfile and enter all the paramertes.

# Process
1) create DB if not present at destination
2) generate list of table from the source DB
3) Take dump of source DB roles and restore to the destination Db
4) Take dump of source DB schema and restore to the destination DB
5) Migrate the data from each table in order of table.txt file using \copy command.

This script use python mulitprocessing which do migration in parallel. So there might be load on the box but script
automatically finalise the capacity and generate process according to it.

If you want to change it to multithread then go to data_migration_multiprocessing.py file and change processexector to ThreadPoolExecutre.
It will use then multithreading at place of multiprocessing.

