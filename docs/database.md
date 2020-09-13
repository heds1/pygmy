# Accessing the database

## Introduction

Pygmy automatically creates a SQLite database when the package is first run.
Database queries are handled by the Python Standard Library package
[sqlite3](https://docs.python.org/3/library/sqlite3.html), which is a standard
Python interface for SQLite databases.

To learn more about interacting with SQLite databases via Python,
[SQLiteTutorial.net](https://www.sqlitetutorial.net/sqlite-python/) is a great resource.

## Database schema

There are two tables in the SQLite database: `messages` and `attachments`.

### Messages

The messages table comprises the following variables:

#### id
- type: `integer primary key`

#### gmail_id
- type: `text NOT NULL UNIQUE`
- description: unique ID given by the Gmail API backend

#### thread
- type: `text`
- description: ID of a given thread (conversation, linked messages) given by the Gmail API backend

#### sender_email
- type: `text`
- description: parsed email of the sender of the message

#### sender_name
- type: `text`
- description: parsed name of the sender of the message

#### date
- type: `text`
- description: date and time the message was sent

#### subject
- type: `text`
- description: subject line of the message

#### body
- type: `text`
- description: content of the message parsed by Beautiful Soup.

### Attachments

TODO

## Direct access via the terminal

If you've got this far, sqlite should already be installed.

From your terminal, in the root pygmy directory, open sqlite:
```
$ sqlite3
```

Connect to the database:
```
sqlite> .open db.sqlite
```

List the database tables:
```
sqlite> .tables
```

You can then run typical SQL queries:
```
sqlite> SELECT * FROM messages;
```

```
sqlite> SELECT filename FROM attachments;
```

End the program:
```
sqlite> .quit
```