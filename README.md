# In development - not released

# Pygmy

Pygmy is a command-line tool used to backup email messages. It uses Gmail's API to find and retrieve messages for an authenticated account.


# Quick start

## Installing dependencies

- Pygmy was built using Python 3.8.
- Firstly, create a virtual environment and activate it:
```
python3 -m venv env
source env/bin/activate
```

- Install the required packages:
```
pip install -r requirements.txt
```

## Authenticating the Gmail account

- Navigate to the Gmail API Python quickstart documentation [here](https://developers.google.com/gmail/api/quickstart/python);
    - click `Enable the Gmail API`
    - select `Desktop app` drop the dropdown menu
    - download the `credentials.json` file
    - and store it in the working directory of the project.

- Run `quickstart.py`:
```
python3 quickstart.py
```
- A browser window should open asking for your credentials. Upon authentication,
a persistent token is created.

# Usage

- Run the program from the root pygmy directory using the default parameters:
```
$ python -m pygmy

Pygmy started: requesting 5 messages...
5 messages retrieved successfully!
```

- Specify a number of messages different to the default (five most recent messages)
with the -n flag:

```
$ python -m pygmy -n 2

Pygmy started: requesting 2 messages...
2 messages retrieved successfully!
```

TODO: Further information can be found in /docs/usage.md

# Contributors
- [Hedley Stirrat](https://github.com/heds1) 
- [Abhishek Chhibber](https://github.com/abhishekchhibber) wrote the original [Gmail-API-through-Python](https://github.com/abhishekchhibber/Gmail-Api-through-Python), and did a better job than the Google API documentation of showing how to retrieve and decode email objects. Some of his code probably lives on in this project today.



