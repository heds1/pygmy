from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import base64
import email
import json # for json dump
import sys  # for json dump
from bs4 import BeautifulSoup
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class MessageHandler:

    def get_message_ids(self, service, user_id='me', n=10):
        """
        return email message ids

        ARGS
            service: 
                authorized Gmail API service instance
            user_id: 
                user's email address. the special value
                "me" can be used to indicate the authenticated user.
            n: 
                number of message ids to retrieve (from most recent).

        RETURNS:
            a list of message ids
        """
        try:
            message_list = service.users().messages().list(userId=user_id, maxResults=n).execute()
            message_ids = [i['id'] for i in message_list['messages']]
            return(message_ids)
        except:
            print('An error occurred retrievign the message IDs.')


    def get_message_content(self, service, user_id, msg_id):
        """
        retrieves the content of an email message, including metadata.

        ARGS:
            service: 
                authorized Gmail API service instance.
            user_id: user's email address. the special value
                "me" can be used to indicate the authenticated user.
            msg_id: the id of the email message to retrieve.
        """

        message_dict = {}
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        # get message headers for metadata
        message_headers = message['payload']['headers']

        # turn list of dicts into single key/value pair dict
        message_headers_ = {d['name']:d['value'] for d in message_headers}

        # retrieve message metadata
        message_dict['from'] = message_headers_['From']
        message_dict['date'] = message_headers_['Date']
        message_dict['subject'] = message_headers_['Subject']

        # for rich-text (HTML-type) messages (?), message['payload']['parts']
        # is a list of length 2. The first element comprises
        # the mimeType: 'text/plain', while the second is mimeType: 'text/html'.
        # both elements are dicts of length 5, containing 'body', 'filename',
        # 'headers', 'mimeType' and 'partId' keys.
        # however, other types of messages do not have a ['payload']['parts']
        # heirarchy.

        if 'parts' in message['payload'].keys():
            try:
                message_content = message['payload']['parts']
            except:
                print('unexpected error')

            # not all messages have the same type. so firstly, gather a list
            # of the mimeTypes in the given message
            mime_types = []
            for i in range(0, len(message_content)):
                mime_types.append(message_content[i].get('mimeType'))

            # then handle depending on type. presumably the types have their own
            # constant heirarchy. TODO this should be formalized in a function
            # elsewhere..
            if 'text/html' in mime_types:
                msg_index = mime_types.index('text/html')
                message_body = message_content[msg_index]['body']['data']
                message_type = 'text/html'
            elif 'text/plain' in mime_types:
                msg_index = mime_types.index('text/plain')
                message_body = message_content[msg_index]['body']['data']
                message_type = 'text/plain'
            elif 'multipart/alternative' in mime_types:
                msg_index = mime_types.index('multipart/alternative')
                if message_content[msg_index].get('parts')[0]['mimeType'] == 'text/plain':
                    message_body = message_content[msg_index].get('parts')[0]['body']['data']
                    message_type = 'text/plain'
                else:
                    print('cant parse message')
        
        # otherwise, we have a different type of message -- should be able
        # to access 'body' directly
        elif 'body' in message['payload'].keys():
            message_body = message['payload']['body']['data']
            message_type = message['payload']['mimeType']

        else:
            print('oh shit')
        
        message_dict['body'] = self.decode_message_body(message_body)
        message_dict['type'] = message_type

        return(message_dict)


    def decode_message_body(self, message_body):
        """
        TODO document
        message bodies are retrieved in base64.
        this function decodes to UTF-8.
        """
        message_body = message_body.replace("-","+")
        message_body = message_body.replace("_","/") 
        message_body = base64.b64decode(bytes(message_body, 'UTF-8'))
        message_body = BeautifulSoup(message_body, "html.parser")
        
        return(message_body.get_text(separator = ' '))


class Service:

    def instantiate_service(self):
        """
        Instantiates a Gmail API service based on stored credentials
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

        return(service)


def main():
    """
    TODO document.
    """
    srv = Service()
    service = srv.instantiate_service()

    handler = MessageHandler()
    
    # get latest 10 message ids
    latest_ids = handler.get_message_ids(service=service, user_id='me', n=10)

    # instantiate list of messages
    retrieved_messages = []

    # loop over messages and append to retrieved_messages list
    for id in latest_ids:
        retrieved_messages.append(handler.get_message_content(service, 'me', id))

    # write to json file
    j = json.dumps(retrieved_messages, indent=4)
    f = open('sample2.json', 'w')
    print(j, file = f)
    f.close()

if __name__ == '__main__':
    main()





