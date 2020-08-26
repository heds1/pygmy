# In development - not released

# Pygmy

Pygmy is a command-line tool used to backup email messages. It uses Gmail's API to find and retrieve messages for an authenticated account.


# Quick start

## Installing Pygmy and dependencies

- Pygmy was built using Python 3.8.
- Firstly, clone the project files:
```
git clone https://github.com/heds1/pygmy.git
```
(this will create a `pygmy` folder in your working directory.)

- Navigate into the pygmy directory and create a Python virtual environment, then activate it:
```
cd pygmy
python3 -m venv env
source env/bin/activate
```

- Create a folder to keep track of the authorization credentials for the API:

```
mkdir .auth
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
    - and store it in the `.auth` folder. If you are forking this project, make sure that the authorization credentials are not committed into version control. (The `.auth` subdirectory is ignored by default, but if you move it, this could be an issue.)

# Quickstart

- Run the program from the root pygmy directory using the default parameters:
```
$ python -m pygmy
```

If this is the first time, a browser window should open asking for your credentials. Upon authentication,
a persistent token is created in the `.auth` directory.
If authentication is successful, you should see the following messages:

```
Pygmy started: requesting 5 messages...
5 messages retrieved successfully!
```

# Usage

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



