Each fridge has its own .db file.

## Adding a column to the database file

The convention is to leave the default value as `NULL`. If a particular column will be no longer monitored, the fill-values will simply be NULL. The idea is that changes to the FridgeParameters JSON will be additive to the database.


