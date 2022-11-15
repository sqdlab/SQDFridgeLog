# SQLite3 Implementation

Here each fridge has its own database .db file. The database is divided into one table (each with time-value pairs) for every parameter that is to be recorded. This because sensors are not all recorded/read concurrently. The times are given as UNIX/POSIX integer time-stamps rounded off to the nearest second. The advatages of this implementation are:

- Does not require a dedicated server
- Only requires vanilla Python3 with numpy installed as it already bundles *SQLite3*.

The disadvantage is that fast/simultaneous queries with the database file stored in a network share will cause errors as the database is locked for any given query (for there is no server to handle queuing). This will cause database locked issues with Grafana. In addition, querying large swathes of data can be slow if done across the network share.


## Installation Instructions

This installation procedure needs to be done once on every individual fridge PC. On the given fridge PC, navigate to a folder to house the script and then clone this repository (installing GIT if required):

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

Now prepare, install and activate a virtual environment. The instructions differ depending on the operating system.

### Windows 7 and above

This works for any OS supporting Python 3. The instructions differ depending on whether one chooses to use Anaconda or Normal Python. If using Anaconda:

```
#Installation
conda create -n sqdfridge_env python=3.9
activate sqdfridge_env
pip install numpy

#Runtime
activate sqdfridge_env
cd C:/Users/....../myFolder/SQDFridgeLog
python Main.py
```

If using Normal Python

```
#If using Normal Python
cd pathToEnvironment
python3 -m venv sqdfridge_env
sqdfridge_env\Scripts\activate
pip install numpy

#Runtime
pathToEnvironment\sqdfridge_env\Scripts\python.exe C:/Users/....../myFolder/SQDFridgeLog/Main.py
```

### Windows XP

Fortunately Python 3 works with the last supported version being 3.4. First install [Python 3.4.3](https://www.python.org/downloads/release/python-343/) via the x86 installer (installing into C:/Python34 for convenience). Run:

```
C:\Python34\python.exe -m pip install numpy
```

Note that one can modify this to run in a venv like in the previous section if desired. If the above fails, then download `numpy‑1.16.6+vanilla‑cp34‑cp34m‑win32.whl` from [Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy). Then navigate to the downloaded folder and run:

```
pip install numpy‑1.16.6+vanilla‑cp34‑cp34m‑win32.whl
```

Now to run the script:

```
cd C:/Users/....../myFolder/SQDFridgeLog
C:\Python34\python.exe Main.py
```

## Usage

Upon creating the configuration file outlined in the previous section, simply run the script in command line (after navigating to the folder `SQDFridgeLog`):

```
python Main.py
```

The script will update the database over an interval given by the `"Polling Interval"` parameter in the JSON configuration file. It will create the database file and an accompanying JSON file. This JSON file has metadata that may be useful in the dashboard (although one may enter the parameters manually, it can still serve as a guide for the frontend developer).

## Database format

The *SQLite3* database created for every fridge has the following attributes:

- A set of tables for every recorded parameter
- Each table has two columns outlining an integer UNIX/POSIX timestamp (rounded to seconds) and the value of the parameter
- The tables may not be necessarily temporally coherent as the logged values typically have different polling intervals for different sensors
- The accompanying JSON file gives a more sensible display label for the associated table name along with the parameters' units.

The database files are unique to every fridge, so there should not be any write-conflicts and dashboards *should* be able to concurrently read.


