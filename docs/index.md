# Flags

## -n
Number of messages to retrieve (from most recent). Defaults to 5.

Retrieve the 10 most recent messages:
```
$ python pygmy -n 10
```

Note that messages are not overwritten or updated; if any of the `-n` messages 
are already stored in the database, these will be ignored.

## -c
TODO