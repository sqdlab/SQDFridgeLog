from FridgeParsers.ParserBluFors import ParserBluFors
from FridgeParsers.ParserOxfordVC import ParserOxfordVC
MySQLsupport = True
try:
    from FridgeDatabaseMySQL import FridgeDatabaseMySQL
except ImportError:
    MySQLsupport = False
import os, json

assert os.path.exists('config.json'), "Must create config.json first - please read Installation Instructions in Readme.md!"
with open('config.json') as json_file:
    confs = json.load(json_file)

if confs['Fridge Type'] == 'OxfordVC':
    fridgeParser = ParserOxfordVC('FridgeParameters/OxfordVC.json', confs['Fridge Log Location'], confs.get("Lowercase", False))
elif confs['Fridge Type'] == 'BluFors':
    fridgeParser = ParserBluFors('FridgeParameters/BluFors.json', confs['Fridge Log Location'], confs.get("Lowercase", False))
else:
    assert False, "Fridge type {0} unsupported!".format(confs['Fridge Type'])

if "Database File Path" in confs:
    fdb = FridgeDatabaseMySQL(confs['Database File Path'], fridgeParser)
else:
    assert MySQLsupport, "Must install mysql.connector.python from pip."
    fdb = FridgeDatabaseMySQL(confs, fridgeParser)
fdb.update_continuously(confs.get('Polling Interval', 30))
