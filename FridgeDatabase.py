import sqlite3
import datetime
import time
import os
import numpy as np

class FridgeDatabase:
    def __init__(self, db_filepath, fridgeParser):
        db_filepath = os.path.realpath(db_filepath).replace('\\','/')

        self._dbfile = db_filepath
        self._fridgeParser = fridgeParser
        
        #Write database metadata
        fridgeParser.writeTranslationJSON(db_filepath)

        #Get database table names for each required parameter...
        cur_tables = fridgeParser.getDBtables()
        #
        db = sqlite3.connect(self._dbfile)
        cur = db.cursor()
        for cur_table in cur_tables:
            cmd = "CREATE TABLE IF NOT EXISTS {0} (  \
                time INTEGER DEFAULT 0 NOT NULL UNIQUE,    \
                value REAL DEFAULT NULL    \
            )".format(cur_table)
            cur.execute(cmd)
        try:
            db.commit()
        except:
            print("Database locked - will try updating next round.")
        db.close()
        a=0

    def _datetime_to_sqlstr(self, objDateTime):
    #    return '\'' + str(objDateTime).replace(' ','T') + '\''
        return int(time.mktime(objDateTime.timetuple()))     #Convert to unix time-stamp


    def _sqlstr_to_datetime(self, strDateTime):
    #    return datetime.datetime(*[int(x) for x in strDateTime.replace('T',' ').replace(' ','-').replace(':','-').split('-')])
        return datetime.datetime.fromtimestamp(strDateTime)
    
    def _update(self):
        db = sqlite3.connect(self._dbfile)
        cur = db.cursor()
        
        #Get tables currently in database
        cur.execute('SELECT name from sqlite_master where type= "table"')
        cur_tables = [x[0] for x in cur.fetchall()]
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
            for cur_entry in new_data[cur_dbTable]:
                if not np.isfinite(cur_entry[1]):
                    continue
                try:
                    cur.execute('insert into {0} values ({1}, {2})'.format(cur_dbTable, self._datetime_to_sqlstr(cur_entry[0]), cur_entry[1]))
                except:
                    continue

        db.commit()
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

