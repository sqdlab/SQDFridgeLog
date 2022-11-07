# Database Notes

## SQLite3

Each fridge has its own .db file.

## Adding a column to the database file

The convention is to leave the default value as `NULL`. If a particular column will be no longer monitored, the fill-values will simply be NULL. The idea is that changes to the FridgeParameters JSON will be additive to the database.

## MySQL

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

