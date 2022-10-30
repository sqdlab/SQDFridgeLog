# SQDFridgeLog - a Dilution Fridge Logger

SQDFridgeLog is a fridge logging software that consolidates the automated logs from computers interfacing with dilution fridges.

Issue:
- Every dilution fridge PC has its own logging format (e.g. BluFors or Oxford)
- Perusing the logs is cumbersome and very slow in some cases (e.g. old PCs running Windows XP)
- A lot of dashboard softwares prefer a dedicated database format like *SQLite3*

SQDFridgeLog solves these issues via:

- A simple vanilla **Python3** script (even compatible with Windows XP)
- Extensible parser framework that accounts for different formats
- Automatically polls for changes in the logs and updates a unique *SQLite3* database and a JSON file with extra metadata information.

Each fridge's dedicated PC will run this script and save logging data into a central location (e.g. a network share). This central database can be read into a dashboard (e.g. Grafana, Dash-Plotly or a more vanilla QT/Tkinter GUI). Currently supported fridge parsers include:

- Oxford `.vcl` format (type: `OxfordVC`)
- BluFors `.log` format (type: `BluFors`)

## Installation Instructions

Just navigate to a folder to house the script and then clone this repository:

```
cd C:/Users/....../myFolder/
git clone https://github.com/sqdlab/SQDFridgeLog.git
```

Now create a file `config.json` in the cloned folder named `SQDFridgeLog` (i.e. in the same folder as `Main.py`). The contents of this file can be edited off this template:

```json
{
    "Fridge Log Location" : "C:/BluForsLogs/",
    "Database File Path" : "F:/path_to_db/BluForsSD.db",
    "Fridge Type" : "OxfordVC",
    "Polling Interval" : 30
}
```

Note the following about the parameters:
- `"Fridge Log Location"` - the folder where the actual log files live. For example, in the BluFors logs, this folder contains the time-stamped folders (e.g. `'22-04-10'`) containing the individual log files. For the Oxford fridges, this would be the folder where all the `.vcl` files live.
- `"Database File Path"` - the full file path to the database file (the script will create one if it does not exist - **ensure it is a unique file name**).
- `"Fridge Type"` - the parser used to interpret the log files (currently supports `"OxfordVC"` and `"BluFors"`)
- `"Polling Interval"` - the database update time given in seconds (i.e. database is updated every 30s in the above example). If this is not supplied, it defaults to 30s.

## Usage

Upon creating the configuration file outlined in the previous section, simply run the script in command line (after navigating to the folder `SQDFridgeLog`):

```
python Main.py
```

The script will update the database over an interval given by the `"Polling Interval"` parameter in the JSON configuration file. It will create the database file and an accompanying JSON file. This JSON file has metadata that may be useful in the dashboard (although one may enter the parameters manually, it can still serve as a guide for the frontend developer).

## Database format

The *SQLite3* database created for every fridge has the following attributes:

- A set of tables for every recorded parameter
- Each table has two columns outlining a SQL timestamp and the value of the parameter
- The tables may not be necessarily temporally coherent as the logged values typically have different polling intervals for different sensors
- The accompanying JSON file gives a more sensible display label for the associated table name along with the parameters' units.

The database files are unique to every fridge, so there should not be any write-conflicts and dashboards should be able to concurrently read.
