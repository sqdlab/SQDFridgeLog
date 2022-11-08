import mysql.connector
import datetime
import time
import os
import numpy as np

class FridgeDatabaseMySQL:
    def __init__(self, confs, fridgeParser):
        self._dbname = confs['Database'].lower()
        self._confs = confs
        self._fridgeParser = fridgeParser
        
        #Write database metadata
        # fridgeParser.writeTranslationJSON(db_name)

        #Get database table names for each required parameter...
        cur_tables = fridgeParser.getDBtables()
        #
        db = mysql.connector.connect(user=self._confs["User"], password=self._confs["Password"],
                                     host=self._confs["Host"],buffered=True)
        cur = db.cursor()
        cur.execute("show databases")
        dbs = [databases[0] for databases in cur]
        #Create database if it does not exist
        if not self._dbname in dbs:
            cur.execute("CREATE DATABASE {0};".format(self._dbname))
        
        cur.execute("USE {0};".format(self._dbname))
        for cur_table in cur_tables:
            cmd = "CREATE TABLE IF NOT EXISTS {0} (  \
                time INTEGER DEFAULT 0 NOT NULL UNIQUE,    \
                value REAL DEFAULT NULL    \
            )".format(cur_table)
            cur.execute(cmd)
        db.close()
        a=0

    def _datetime_to_sqlstr(self, objDateTime):
    #    return '\'' + str(objDateTime).replace(' ','T') + '\''
        return int(time.mktime(objDateTime.timetuple()))     #Convert to unix time-stamp


    def _sqlstr_to_datetime(self, strDateTime):
    #    return datetime.datetime(*[int(x) for x in strDateTime.replace('T',' ').replace(' ','-').replace(':','-').split('-')])
        return datetime.datetime.fromtimestamp(strDateTime)
    
    def _update(self):
        db = mysql.connector.connect(user=self._confs["User"], password=self._confs["Password"],
                                     host=self._confs["Host"],buffered=True)
        cur = db.cursor()
        cur.execute("USE {0};".format(self._dbname))
        
        #Get tables currently in database
        cur.execute('SHOW TABLES')
        cur_tables = [x[0] for x in cur]
        last_table_times = {}
        #Fetch last time-stamps
        for cur_table in cur_tables:
            cur.execute('SELECT * FROM {0} ORDER BY time DESC LIMIT 1;'.format(cur_table))
            last_time = cur.fetchall()
            if len(last_time) == 0:
                last_time = datetime.datetime(1900,1,1)
            else:
                last_time = self._sqlstr_to_datetime(last_time[0][0])
            last_table_times[cur_table] = last_time

        new_data = self._fridgeParser.getNewData(last_table_times)
        
        for cur_dbTable in new_data:
            # try:    #Mainly for uniqueness issues... Happens because of integer POSIX vs. real POSIX...
            # sql ="INSERT INTO {0}(time,value) VALUES (%s, %s)".format(cur_dbTable)
            batches = [str((self._datetime_to_sqlstr(x[0]), x[1])) for x in new_data[cur_dbTable] if np.isfinite(x[1])]
            if len(batches) == 0:
                continue
            # cur.executemany(sql, batches)
            strE = "INSERT IGNORE INTO {0}(time,value) VALUES ".format(cur_dbTable) + ','.join(batches)
            cur.execute(strE)
            db.commit()
            # except:
            #     continue

        db.close()

    def update_continuously(self, poll_delay_seconds=30):
        while(True):
            self._update()
            poll_delay_seconds = int(poll_delay_seconds)
            disp = '|'
            last_time = datetime.datetime.now()
            for m in range(poll_delay_seconds):
                if disp == '|':
                    disp = '-'
                else:
                    disp = '|'
                time.sleep(1)
                print('Last Updated: {0} {1}'.format(last_time, disp), end="\r")

