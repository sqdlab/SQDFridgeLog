import sqlite3
import datetime
import time
import os

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
            cmd = f"CREATE TABLE IF NOT EXISTS {cur_table} (  \
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL UNIQUE,    \
                value REAL DEFAULT NULL    \
            )"
            cur.execute(cmd)
        db.commit()
        db.close()
        a=0

    def _datetime_to_sqlstr(self, objDateTime):
       return '\'' + str(objDateTime).replace(' ','T') + '\''

    def _sqlstr_to_datetime(self, strDateTime):
       return datetime.datetime(*[int(x) for x in strDateTime.replace('T',' ').replace(' ','-').replace(':','-').split('-')])
    
    def _update(self):
        db = sqlite3.connect(self._dbfile)
        cur = db.cursor()
        
        #Get tables currently in database
        cur.execute(f'SELECT name from sqlite_master where type= "table"')
        cur_tables = [x[0] for x in cur.fetchall()]
        last_table_times = {}
        #Fetch last time-stamps
        for cur_table in cur_tables:
            cur.execute(f'SELECT * FROM {cur_table} ORDER BY time DESC LIMIT 1;')
            last_time = cur.fetchall()
            if len(last_time) == 0:
                last_time = datetime.datetime(1900,1,1)
            else:
                last_time = self._sqlstr_to_datetime(last_time[0][0])
            last_table_times[cur_table] = last_time

        new_data = self._fridgeParser.getNewData(last_table_times)
        
        for cur_dbTable in new_data:
            for cur_entry in new_data[cur_dbTable]:
                try:
                    cur.execute(f'insert into {cur_dbTable} values ({self._datetime_to_sqlstr(cur_entry[0])}, {cur_entry[1]})')
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
                print(f'Last Updated: {last_time} {disp}', end="\r")

