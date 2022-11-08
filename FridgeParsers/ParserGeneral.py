import json
import os

class ParserGeneral:
    def getNewData(self, lastTimeStamps={}):
        '''
        Function that returns a dictionary of fridge parameters.
        '''
        raise NotImplementedError()

    def getDBtables(self):
        assert hasattr(self, '_config_data'), "Derived class must implement attribute _config_data where it loads the JSON file..."
        return [self._config_data['parameters'][cur_key]['db'] for cur_key in self._config_data['parameters']]

    def writeTranslationJSON(self, filepath):
        dirName = os.path.dirname(filepath) + '/'
        fileName = os.path.basename(filepath)[:-3]
        json_data = {self._config_data['parameters'][x]['db'] : {'label': x, 'unit' : self._config_data['parameters'][x].get('unit','')} for x in self._config_data['parameters']}
        with open(dirName + fileName + '.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=4)

    def load_config_JSON(self, config_file, lowercase_names = False):
        with open(config_file) as json_file:
            self._config_data = json.load(json_file)
        if lowercase_names:
            for cur_param in self._config_data['parameters']:
                self._config_data['parameters'][cur_param]['db'] = self._config_data['parameters'][cur_param]['db'].lower()
