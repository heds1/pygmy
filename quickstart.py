from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from bs4 import BeautifulSoup
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # get a list of the 5 most recent messages
    # this does NOT retrieve the actual message data,
    # we just use it to get the IDs
    message_list = service.users().messages().list(userId='me', maxResults=5).execute()
    message_ids = [i['id'] for i in message_list['messages']]

    # instantiate list to populate with clean messages
    clean_messages = []

    # loop over the message IDs to retrieve each actual message
    for m in message_ids:

        # instantiate empty dict to hold message content
        message_dict = {}

        # retrieve the actual message
        message = service.users().messages().get(userId='me', id=m).execute()

        # get message headers for metadata
        message_headers = message['payload']['headers']

        # turn list of dicts into single key/value pair dict
        message_headers_ = {d['name']:d['value'] for d in message_headers}

        # retrieve message metadata
        message_dict['from'] = message_headers_['From']
        message_dict['date'] = message_headers_['Date']
        message_dict['subject'] = message_headers_['Subject']

        # make this a try.
        # maybe parts is only for rich-text.
        # e.g. a github email in plain text has no parts.
        
        # retrieve message content - go in via parts for some reason
        message_content = message['payload']['parts']
        part_one  = message_content[0] # fetching first element of the part 
        part_body = part_one['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
        message_body = BeautifulSoup(clean_two , "html.parser" )
        message_dict['body'] = message_body

        # append to list of compiled messages
        clean_messages.append(message_dict)
        # todo download conditionally on unread/read (label??)

    print('lol')

if __name__ == '__main__':
    main()
