# Accessing the database

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