from FridgeParsers.ParserBluFors import ParserBluFors
from FridgeParsers.ParserOxfordVC import ParserOxfordVC
from FridgeDatabase import FridgeDatabase
import os, json

assert os.path.exists('config.json'), "Must create config.json first - please read Installation Instructions in Readme.md!"
with open('config.json') as json_file:
    confs = json.load(json_file)

if confs['Fridge Type'] == 'OxfordVC':
    fridgeParser = ParserOxfordVC('FridgeParameters/OxfordVC.json', confs['Fridge Log Location'])
elif confs['Fridge Type'] == 'BluFors':
    fridgeParser = ParserBluFors('FridgeParameters/BluFors.json', confs['Fridge Log Location'])
else:
    assert False, "Fridge type {0} unsupported!".format(confs['Fridge Type'])

fdb = FridgeDatabase(confs['Database File Path'], fridgeParser)
fdb.update_continuously()
