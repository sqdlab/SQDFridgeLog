# MySQL Implementation

Here a dedicated computer on the network hosts a *MySQL* database server. Each fridge stores its data in its own MySQL database. Each database is divided into one table (each with time-value pairs) for every parameter that is to be recorded. This because sensors are not all recorded/read concurrently. The times are given as UNIX/POSIX integer time-stamps rounded off to the nearest second. The advatages of this implementation are:

- Robust to multiple or simultaneous queries as the server activately queues and manages the queries.
- Fast; even for large queries. Thus, it does not have locking issues unlike the *SQLite3* implementation.

The disadvantage is that it requires a dedicated server.


## Installation (Server Side)

This highlights the server-side installation. Go the [MySQL page](https://dev.mysql.com/downloads/installer/) and download the *Windows (x86, 32-bit), MSI Installer*. Note that there is no need to sign into an account; just download the installer. Then install everything (ensuring that services is ticked so that it autostarts). During the server installation, ensure that a sensible root account and password is chosen. Now the issue is:

- Root only has access to *localhost* for [security reasons](https://support.infrasightlabs.com/troubleshooting/host-is-not-allowed-to-connect-to-this-mysql-server/)
- To interface with clients, there needs to be a separate admin account

To create one, first setup the query window in MySQL Workbench (after logging into the root account). Then setup the following script and run (noting that `<password>` is a custom password and `<user>` is a custom user name):

```sql
CREATE USER '<user>'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON *.* TO '<user>'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

The `'%'` makes it so that it works on all IP address ranges. To see if it worked, run:

```sql
SELECT host FROM mysql.user WHERE User='<user>' LIMIT 0, 1000
```

It should show `'%'` (among others like the server IP and localhost). If there are still issues, try opening the [Windows Firewall](https://gist.github.com/egalink/c4edd08b664fd1a04785eec7dee43fed) for TCP Port 3306. Now the clients can create/edit databases via `<user>` and `<password>`.


## Installation (Client Side)

This installation procedure needs to be done once on every individual fridge PC. On the given fridge PC, navigate to a folder to house the script and then clone this repository (installing GIT if required):

```
cd C:/Users/....../myFolder/
git clone https://github.com/sqdlab/SQDFridgeLog.git
```

Now create a file `config.json` in the cloned folder named `SQDFridgeLog` (i.e. in the same folder as `Main.py`). The contents of this file can be edited off this template:

```json
{
    "Fridge Log Location" : "C:/Oxford Instruments/logfiles/nobody/",
    "Database" : "oxford",
    "User"     : "<user>",
    "Password" : "<password>",
    "Host"     : "<ip address>",
    "Fridge Type" : "OxfordVC",
    "Lowercase": true,
    "Polling Interval" : 5
}
```

Note the following about the parameters:
- `"Fridge Log Location"` - the folder where the actual log files live. For example, in the BluFors logs, this folder contains the time-stamped folders (e.g. `'22-04-10'`) containing the individual log files. For the Oxford fridges, this would be the folder where all the `.vcl` files live.
- `"Database"` - the database name to which the current fridge's data is to be stored (the script will create one if it does not exist - **ensure it is a unique name**).
- `"User"` and `"Password"` - the same `<user>` and `<password>` used in the server-side installation.
- `"Host"` - IP address of the server (noting that it uses its default port)
- `"Fridge Type"` - the parser used to interpret the log files (currently supports `"OxfordVC"` and `"BluFors"`)
- `"Lowercase"` - mostly the server defaults to converting all database table names and parameters to lowercase when storing and querying. This may cause issues with the Python scripts; so if this behvaiour has been set, set this parameter to be `true`.
- `"Polling Interval"` - the database update time given in seconds (i.e. database is updated every 30s in the above example). If this is not supplied, it defaults to 30s.

Now prepare, install and activate a virtual environment. The instructions differ depending on the operating system.

### Windows 7 and above

This works for any OS supporting Python 3. The instructions differ depending on whether one chooses to use Anaconda or Normal Python. If using Anaconda:

```
#Installation
conda create -n sqdfridge_env python=3.9
activate sqdfridge_env
pip install numpy
pip install mysql.connector.python

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
pip install mysql.connector.python

#Runtime
pathToEnvironment\sqdfridge_env\Scripts\python.exe C:/Users/....../myFolder/SQDFridgeLog/Main.py
```

Note that in both cases, ensure that it is **`mysql.connector.python`** and NOT **`mysql.connector`**.

### Windows XP

Fortunately Python 3 works with the last supported version being 3.4. First install [Python 3.4.3](https://www.python.org/downloads/release/python-343/) via the x86 installer (installing into C:/Python34 for convenience). Run:

```
C:\Python34\python.exe -m pip install numpy
C:\Python34\python.exe -m pip install mysql.connector.python==8.0.13
```

Note that one can modify this to run in a venv like in the previous section if desired. If the above numpy installation fails, then download `numpy‑1.16.6+vanilla‑cp34‑cp34m‑win32.whl` from [Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy). Then navigate to the downloaded folder and run:

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

The *MySQL* database created for every fridge has the following attributes:

- A set of tables for every recorded parameter
- Each table has two columns outlining an integer UNIX/POSIX timestamp (rounded to seconds) and the value of the parameter
- The tables may not be necessarily temporally coherent as the logged values typically have different polling intervals for different sensors

The databases are unique to every fridge, so there should not be any write-conflicts and dashboards should be able to concurrently read.
