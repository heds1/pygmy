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
import argparse
from cryptography.fernet import Fernet
import sqlite3

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Structure:
# - the Service class instantiates the Gmail API,
# and looks for message IDs etc.

# The Message class does something...


class Service:
    def __init__(self):
        # check for auth folder; create if it doesn't exist
        if not os.path.exists('.auth'):
            os.mkdir('.auth')

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        # if this truly is the first time (i.e. if we don't see
        # credentials.json)...
        if not os.path.exists('.auth/credentials.json'):
            print('Have you enabled the Gmail API? Follow the instructions at https://developers.google.com/gmail/api/quickstart/python to enable the Gmail API, and store the credentials locally.')
            return(0)

        if os.path.exists('.auth/token.pickle'):
            with open('.auth/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '.auth/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('.auth/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        

    def retrieve_ids(self, user_id='me', n=5):
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

            message_list = self.service.users().messages().list(userId=user_id, maxResults=n).execute()
            message_ids = [i['id'] for i in message_list['messages']]
            num_retrieved = len(message_ids)
            
            # if we asked for more than 500 messages (the max for the API call),
            # we need to grab the nextPageToken and repeat the call. also keep track
            # of how many messages have been retrieved so far.
            while num_retrieved < n:
                page_token = message_list['nextPageToken']
                message_list = self.service.users().messages().list(
                    userId=user_id,
                    maxResults=n-num_retrieved,
                    pageToken=page_token
                ).execute()
                [message_ids.append(i['id']) for i in message_list['messages']]
                num_retrieved = len(message_ids)

            print(str(len(message_ids)) + ' messages retrieved successfully!')
            return(message_ids)
        except:
            print('An error occurred retrieving the message IDs.')


class Encryptor:
    # init object by finding key and creating fernet
    def __init__(self):
        if not os.path.exists('.auth/key'):
            key = Fernet.generate_key()
            f = open('.auth/key', 'wb')
            f.write(key)
            f.close()
        
        with open('.auth/key', 'rb') as keyfile:
            self.key = keyfile.read()

        self.fernet = Fernet(self.key)

    def encrypt(self, obj):
        """
        Encrypts a byte object.
        param obj: 
            the object to encrypt.
        """
        # if object is a string, convert to bytes for encryption
        if type(obj) is str:
            obj = obj.encode()
        # encrypt, and convert back to str (so we can write to json)
        obj = decode(self.fernet.encrypt(obj))
        return obj


class Message:
    # instantiate a Message object with just the Gmail ID
    def __init__(self, id):
        self.gmail_id = id
        self.date = None
        self.sender = None
        self.subject = None
        self.body = None
        self.type = None


    def retrieve_message(self, service, user_id):
        """
        Retrieve the JSON representation of an individual message.
        param service: 
            authorized Gmail API service instance.
        param user_id:
            user's email address ('me' indicates authorized user)
        """
        try:
            message = service.users().messages().get(userId=user_id, id=self.gmail_id).execute()
            return message
        except:
            print('Error in Message.retrieve_message()')
            return None


    def parse_headers(self, message):
        """
        Parse the headers of a returned message JSON object.
        param message:
            the returned object of Message.retrieve_message().
        """
        try:
            # get message headers for metadata
            headers = message['payload']['headers']
            # turn list of dicts into single key/value pair dict
            headers = {d['name']:d['value'] for d in headers}
            return headers
        except:
            print('Error in Messsage.parse_headers()')
            return None


    def parse_metadata(self, headers):
        """
        Parse the metadata of a returned message JSON object,
        using the intermediate message headers. saves to Message object.
        param id:
            the gmail_id of the message
        param headers:
            the returned objects of Message.parse_headers().
        return:
            dict containing message metadata ('from', 'date', 'subject')
        """
        try:
            self.date = headers['Date']
            self.sender = headers['From']
            self.subject = headers['Subject']
        except:
            print('Error in Message.parse_metadata()')


    def parse_body(self, payload):
        # for rich-text (HTML-type) messages (?), message['payload']['parts']
        # is a list of length 2. The first element comprises
        # the mimeType: 'text/plain', while the second is mimeType: 'text/html'.
        # both elements are dicts of length 5, containing 'body', 'filename',
        # 'headers', 'mimeType' and 'partId' keys.
        # however, other types of messages do not have a ['payload']['parts']
        # heirarchy.

        if 'parts' in payload.keys():
            try:
                message_content = payload['parts']
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
        elif 'body' in payload.keys():
            message_body = payload['body']['data']
            message_type = payload['mimeType']

        else:
            print('oh shit')
        
        self.body = self.decode(message_body)
        self.type = message_type
        return


    def write_to_json(self):
        j = json.dumps(self.__dict__, indent=4)
        f = open('sample.json', 'a')
        print(j, file = f)
        f.close()


    def decode(self, obj):
        """
        Decode string from base64 to UTF-8;
        parse HTML with BeautifulSoup.
        param obj:
            string to decode.
        """
        obj = obj.replace("-","+")
        obj = obj.replace("_","/") 
        obj = base64.b64decode(bytes(obj, 'UTF-8'))
        obj = BeautifulSoup(obj, "html.parser")
        return(obj.get_text(separator = ' '))


    def write_to_db(self, msg, encrypt):
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        if encrypt:
            # if encrypt 
            body = msg['body'].decode()
        else:
            body = msg['body'].encode()
        # need to decode the values from byte to string
        query = str("INSERT INTO EMAILS (Sender, Date, Subject, Content) VALUES ('" +
                msg['from'] + "', '" + msg['date'] + "', '" +
                msg['subject'] + "', '" + body + "')")
        c.execute(query)
        conn.commit()
        conn.close()


def main():
    """
    TODO document.
    """
    # instantiate argument parser
    parser = argparse.ArgumentParser(description='Retrieve email messages.')

    # specify number of messages to retrieve
    parser.add_argument('-n', type=int, default=5,
        help='number of messages to retrieve. most recent messages are retrieved first. default: 5.')
    
    # optional encryption argument. action='store_true' means
    # it defaults to FALSE if no flag is provided, but if a flag
    # is provided it becomes TRUE (and we need to supply that so that
    # no argument is required, e.g., we don't need to write -e 1).
    parser.add_argument('--e', action='store_true',
        help='encrypt body of the message?')
    args = parser.parse_args()
    if args.e:
        print('encrypting the body of the messages :)')
    else:
        print('NOT encrypting messages.')

    print("Pygmy started: requesting " + str(args.n) + " messages...")

    # instantiate service
    service = Service()       
    
    # instantiate cryptography handler
    if args.e:
        encryptor = Encryptor()

    # get latest n message ids
    latest_ids = service.retrieve_ids(user_id='me', n=args.n)

    # retrieve and save messages
    for id in latest_ids:
        message = Message(id)
        payload = message.retrieve_message(service.service, 'me')
        headers = message.parse_headers(payload)
        message.parse_metadata(headers)
        message.parse_body(payload['payload'])

        if args.e:
            message.body = encryptor.encrypt(message.body)

        message.write_to_json()
    

if __name__ == '__main__':
    main()


        



