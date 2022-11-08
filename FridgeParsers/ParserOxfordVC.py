import enum
from re import L
from .ParserGeneral import ParserGeneral
import json
import os
import numpy as np
import datetime

class ParserOxfordVC(ParserGeneral):
    def __init__(self, config_file, log_directory, lowercase_names = False):
        self._log_dir = log_directory
        self._log_dir = self._log_dir.replace('\\','/')
        if self._log_dir[-1] != '/':
            self._log_dir = self._log_dir + '/'

        #Get configuration data - value for a key is given as the data entry title when parsing the vcl file
        self.load_config_JSON(config_file, lowercase_names)

    def _parse_with_numpy(self, filename, MAX_CHANNELS_COUNT = 52):
        #print(filename)
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
            if data.size == 0:
                return [], []
            return titles, data.reshape((data_item_size, -1), order='F')[1:(len(titles) + 1)]

        with open(filename, 'rb') as f_in:
            return _parse(f_in)

    def getNewData(self, lastTimeStamps={}):
        #Since it's fully tabular, all values are recorded in the same time-stamp - so just take last one...
        #All tables should be updated anyway given that the commit is done after executing all commands so...
        lastTimeStamp = max([lastTimeStamps[x] for x in lastTimeStamps])

        #Get log folders present
        cur_files = [self._log_dir + name for name in os.listdir(self._log_dir) if name.endswith('.vcl')]
        cur_files = [cur_file for cur_file in cur_files if os.path.basename(cur_file)[:4] == 'log ']
        cur_files = sorted(cur_files)

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
        cur_file_ts = [ ( datetime.datetime.strptime(os.path.basename(cur_file)[4:-4], '%y%m%d %H%M%S'), cur_file ) for cur_file in cur_files ]
        for m, cur_file in enumerate(cur_file_ts):
            if cur_file[0] >= lastTimeStamp:
                break
        if m > 0:
            m -= 1
        cur_file_ts = cur_file_ts[m:]

        ret_params = {}
        total_len = 0
        max_per_upload = 10000      #To overcome RAM limitation in 4GB XP computers...
        for _, cur_file in cur_file_ts:
            #Titles appear on rows...
            titles, data = self._parse_with_numpy(cur_file)
            if len(titles) == 0:
                continue
            time_stamps = [datetime.datetime.fromtimestamp(np.round(x)) for x in data[1]]
            sel_inds = [m for m in range(len(time_stamps)) if time_stamps[m] > lastTimeStamp]
            total_len += len(sel_inds)
            if total_len + len(sel_inds) > max_per_upload:
                sel_inds = sel_inds[:(max_per_upload-total_len)]
                if len(sel_inds) == 0:
                    break
                break_now = True
            else:
                break_now = False
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
            if break_now:
                break
        
        return ret_params
