from . ParserGeneral import ParserGeneral
import json
import os
import numpy as np
import datetime

class ParserBluFors(ParserGeneral):
    def __init__(self, config_file, log_directory):
        self._log_dir = log_directory
        self._log_dir = self._log_dir.replace('\\','/')
        if self._log_dir[-1] != '/':
            self._log_dir = self._log_dir + '/'

        #Get configuration data - value for a key is given as: [file-name, label, offset to value]
        #For example, ["Status", "cpatempwi", 1] implies the label "cpatempwi" with the value being
        #the index right after in the comma separated file.
        #
        #If it is given as ["CH6"], then it's just time-value and thus, the value after the last
        #comma is taken...
        with open(config_file) as json_file:
            self._config_data = json.load(json_file)
        
    def getNewData(self, lastTimeStamps={}):
        #Presume that data is strictly stored in time-stamped folders 
        all_folders = next(os.walk(self._log_dir))[1]

        #Collect all files that need to be read to extract all desired parameters
        req_files = [ self._config_data['parameters'][cur_key]['location'][0] for cur_key in self._config_data['parameters'] ]
        req_files = set(req_files)
        ret_params = {}
        #Iterate over each file (i.e. extract all requried parameters from the file instead of opening it multiple times for each parameter)
        for cur_file in req_files:
            #Parameters in a single file are tabular - so just take the minimum time-stamp (they should mostly be the same, but maybe it forgot to enter one of them before...)
            cur_params_in_file = [ self._config_data['parameters'][cur_key]['db'] for cur_key in self._config_data['parameters'] if self._config_data['parameters'][cur_key]['location'][0] == cur_file]
            lastTimeStamp = min([lastTimeStamps[x] for x in cur_params_in_file])

            cur_folders = []
            #Find all relevant data folders...
            for cur_folder in all_folders:
                try:
                    year = int(cur_folder[0:2]) + 2000
                    month = int(cur_folder[3:5])
                    day = int(cur_folder[6:8])
                except:
                    continue
                if lastTimeStamp.year > year:
                    continue
                if lastTimeStamp.month > month:
                    continue
                if lastTimeStamp.day > day:
                    continue
                cur_folders += [cur_folder]
            cur_folders = sorted(cur_folders)

            #Find the folders that contain information to be read...
            for cur_folder in cur_folders:
                cur_path = self._log_dir + cur_folder + '/'
                cand_files = next(os.walk(cur_path))[2]
                leFile = ''
                for cur_cand_file in cand_files:
                    if cur_cand_file.startswith(cur_file):
                        leFile = cur_path + cur_cand_file
                        break
                if leFile == '':
                    continue
                
                #Read all lines that come after lastTimeStamp for the log file inside this current (time-stamped) folder
                relevantLines = []
                with open(leFile) as f:
                    for line in f:
                        cur_timestamp = line.split(',')[:2]
                        cur_timestamp = cur_timestamp[0].split('-')[::-1] + cur_timestamp[1].split(':')
                        cur_timestamp = [int(x) for x in cur_timestamp]
                        cur_timestamp[0] += 2000
                        cur_timestamp = datetime.datetime(*cur_timestamp)
                        if cur_timestamp > lastTimeStamp:
                            relevantLines += [(cur_timestamp, line.split(','))]
                if len(relevantLines) == 0:
                    continue

                #Gather all parameters that are to be read from this file...
                cur_params = [ self._config_data['parameters'][cur_key] for cur_key in self._config_data['parameters'] if self._config_data['parameters'][cur_key]['location'][0] == cur_file]
                for cur_param in cur_params:
                    cur_db = cur_param['db']
                    if not cur_db in ret_params:
                        ret_params[cur_db] = []
                    for cur_line in relevantLines:
                        if len(cur_param['location']) == 3:
                            if cur_param['location'][1] in cur_line[1]:
                                cur_val = float(cur_line[1][cur_line[1].index(cur_param['location'][1])+cur_param['location'][2]])
                            else:
                                continue
                        else:
                            cur_val = float(cur_line[1][-1])
                        ret_params[cur_db] += [(cur_line[0], cur_val)]
        
        return ret_params
        
