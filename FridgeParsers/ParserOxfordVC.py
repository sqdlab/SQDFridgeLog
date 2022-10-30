from re import L
from .ParserGeneral import ParserGeneral
import json
import os
import numpy as np
import datetime

class ParserOxfordVC(ParserGeneral):
    def __init__(self, config_file, log_directory):
        self._log_dir = log_directory
        self._log_dir = self._log_dir.replace('\\','/')
        if self._log_dir[-1] != '/':
            self._log_dir = self._log_dir + '/'

        #Get configuration data - value for a key is given as the data entry title when parsing the vcl file
        with open(config_file) as json_file:
            self._config_data = json.load(json_file)

    def _parse_with_numpy(self, filename, MAX_CHANNELS_COUNT = 52):
        #Code adapted from: https://github.com/StSav012/VeriCold_log_parser
        def _parse(file_handle):
            file_handle.seek(0x1800 + 32)
            titles = [file_handle.read(32).strip(b'\0').decode('ascii') for _ in range(MAX_CHANNELS_COUNT - 1)]
            titles = list(filter(None, titles))
            file_handle.seek(0x3000)
            # noinspection PyTypeChecker
            dt = np.dtype(np.float64).newbyteorder('<')
            data = np.frombuffer(file_handle.read(), dtype=dt)
            i = 0
            data_item_size = None
            while i < data.size:
                if data_item_size is None:
                    data_item_size = int(round(data[i] / dt.itemsize))
                elif int(round(data[i] / dt.itemsize)) != data_item_size:
                    raise RuntimeError('Inconsistent data: some records are faulty')
                i += int(round(data[i] / dt.itemsize))
            return titles, data.reshape((data_item_size, -1), order='F')[1:(len(titles) + 1)]

        with open(filename, 'rb') as f_in:
            return _parse(f_in)

    def getNewData(self, lastTimeStamps={}):
        #Since it's fully tabular, all values are recorded in the same time-stamp - so just take minimum...
        lastTimeStamp = min([lastTimeStamps[x] for x in lastTimeStamps])

        #Get log folders present
        cur_files = [self._log_dir + name for name in os.listdir(self._log_dir) if name.endswith('.vcl')]

        #Used in debugging - i.e. what titles may exist in the VCL files...
        # titles_all = []
        # for cur_file in cur_files:
        #     titles, data = self._parse_with_numpy(cur_file)
        #     titles_all += titles
        # titles_all = sorted(list(set(titles_all)))
        # with open('VCL_Titles.txt', 'w') as f:
        #     for line in titles_all:
        #         f.write(f"{line}\n")

        #The files are named 'log 220923 103837.vcl' - i.e. 'log YYMMDD HHMMSS.vcl' 
        cur_file_ts = []
        for cur_file in cur_files:
            cur_name = os.path.basename(cur_file)
            if cur_name[:4] != 'log ':
                continue
            cur_name = cur_name[4:-4]
            cur_ts = datetime.datetime.strptime(cur_name, '%y%m%d %H%M%S')
            if cur_ts.year < 2000:
                cur_ts = cur_ts.replace(year = cur_ts.year + 100)
            if cur_ts >= lastTimeStamp:
                cur_file_ts += [(cur_ts, cur_file)]
        
        cur_file_ts = sorted(cur_file_ts, key=lambda x: x[0])
        ret_params = {}
        for _, cur_file in cur_file_ts:
            #Titles appear on rows...
            titles, data = self._parse_with_numpy(cur_file)
            time_stamps = [datetime.datetime.fromtimestamp(x) for x in data[1]]
            sel_inds = [m for m in range(len(time_stamps)) if time_stamps[m] >= lastTimeStamp]
            if len(sel_inds) == 0:
                continue
            for cur_param in self._config_data['parameters']:
                cur_db = self._config_data['parameters'][cur_param]['db']
                if not cur_db in ret_params:
                    ret_params[cur_db] = []
                cur_vcl_name = self._config_data['parameters'][cur_param]['location']
                if not cur_vcl_name in titles:
                    continue
                cur_row = titles.index(cur_vcl_name)
                ret_params[cur_db] += [(time_stamps[x], data[cur_row][x]) for x in sel_inds]
        
        return ret_params
