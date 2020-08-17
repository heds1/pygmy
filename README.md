# Pygmy

A Python interface to the Gmail API used to backup and view emails locally.

# Contributors
- [Hedley Stirrat](https://github.com/heds1)
- [Abhishek Chhibber](https://github.com/abhishekchhibber) wrote the original [Gmail-API-through-Python](https://github.com/abhishekchhibber/Gmail-Api-through-Python), and did a better job than the Google API documentation of showing how to retrieve and decode email objects. Some of his code probably lives on in this project today.

# Quick start
This project requires Python 3 and has been tested on Linux Ubuntu 20.04.

Firstly, create a virtual environment and activate it:
```
python3 -m venv env
source env/bin/activate
```

Install the required packages:

```
pip install -r requirements.txt
```

Navigate to the Gmail API Python quickstart documentation [here](https://developers.google.com/gmail/api/quickstart/python).
Click `Enable the Gmail API`, select `Desktop app` drop the dropdown menu, download the `credentials.json` file and
store it in the working directory of the project.

Run quickstart.py, and a browser window should open asking for your credentials:

```
python3 quickstart.py
```

