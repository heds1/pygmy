# Accessing the database

## Introduction

Pygmy automatically creates a SQLite database when the package is first run.
Database queries are handled by the Python Standard Library package
[sqlite3](https://docs.python.org/3/library/sqlite3.html), which is a standard
Python interface for SQLite databases.

To learn more about interacting with SQLite databases via Python,
[SQLiteTutorial.net](https://www.sqlitetutorial.net/sqlite-python/) is a great resource.

## Direct access via the terminal

If you've got this far, sqlite should already be installed.

From your terminal, in the root pygmy directory, open sqlite.:
```
$ sqlite
```

Connect to the database:
```
sqlite> .open db.sqlite
```

You can then run typical SQL queries:
```
sqlite> SELECT * FROM messages;
```