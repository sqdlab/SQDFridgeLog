# SQDFridgeLog - a Dilution Fridge Logger

SQDFridgeLog is a fridge logging software that consolidates the automated logs from computers interfacing with dilution fridges.

Issue:
- Every dilution fridge PC has its own logging format (e.g. BluFors or Oxford)
- Perusing the logs is cumbersome and very slow in some cases (e.g. old PCs running **Windows XP**)
- A lot of dashboard softwares prefer a dedicated database format like *SQLite3* or *MySQL*

SQDFridgeLog solves these issues via:

- A simple vanilla **Python3** script (even compatible with Windows XP)
- Extensible parser framework that accounts for different formats
- Automatically polls for changes in the logs and updates a unique *SQLite3* or *MySQL* database.

Each fridge's dedicated PC will run the client-side script and save logging data into a central location (e.g. a network share or a server). This central database can be read into a dashboard (e.g. Grafana, Dash-Plotly or a more vanilla QT/Tkinter GUI). Currently supported fridge parsers include:

- Oxford `.vcl` format (type: `OxfordVC`)
- BluFors `.log` format (type: `BluFors`)

The implementation has two flavours:

- [SQLite3](Documentation/InstallationSQLite3.md) - simplest implementation that only requires access to some storage location (no dedicated server required)
- [MySQL](Documentation/InstallationNotesMySQL.md) - a more robust implementation that requires access to a dedicated server running MySQL.

Both flavours are suitable for clients running anything from Windows XP onwards.
