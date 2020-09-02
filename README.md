<color:red>Pygmy is in development and is not in a stable release.</color>

# Pygmy

Pygmy is a command-line tool used to backup email messages.
It uses Gmail's API to find and retrieve messages for an authenticated account.

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

- Install sqlite
    - Debian/Ubuntu:
    ```
    sudo apt install sqlite3
    ```

## Authenticating the Gmail account

- Navigate to the Gmail API Python quickstart documentation [here](https://developers.google.com/gmail/api/quickstart/python);
    - click `Enable the Gmail API`
    - select `Desktop app` drop the dropdown menu
    - download the `credentials.json` file
    - and store it in the `.auth` folder. If you are forking this project, make sure that the authorization credentials are not committed into version control. (The `.auth` subdirectory is ignored by default, but if you move it, this could be an issue.)

- Run the package from the root pygmy directory using the default parameters:
```
$ python pygmy
```

If this is the first time, a browser window should open asking for your credentials. Upon authentication,
a persistent token is created in the `.auth` directory.
If authentication is successful, you should see the following messages:

```
Pygmy started: requesting 5 messages...
5 messages retrieved successfully!
```

Refer to the [user guide](https://github.com/heds1/pygmy/blob/master/docs/index.md) 
for further documentation.

## Contributors
- [Hedley Stirrat](https://github.com/heds1) is the author of Pygmy.
- [Abhishek Chhibber](https://github.com/abhishekchhibber) wrote the original [Gmail-API-through-Python](https://github.com/abhishekchhibber/Gmail-Api-through-Python), and his code helped this project get off the ground.