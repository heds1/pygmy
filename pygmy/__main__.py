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
        

    def retrieve_ids(self, user_id='me', n=10):
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



class CryptHandler:
    
    def get_key(self):
        """
        check that decryption key is found. if not, create it.
        """
        if not os.path.exists('.auth/key'):
            key = Fernet.generate_key()
            f = open('.auth/key', 'wb')
            f.write(key)
            #print(key, file = f)
            f.close()
        
        with open('.auth/key', 'rb') as keyfile:
            key = keyfile.read()

        return(key)
     

    def encrypt_message(self, key, msg, fernet):
        """
        encrypts an email message.
        only encrypts the body of the message,
        not the metadata!
        ARGS:
            key - secret key
        """
        msg['body'] = fernet.encrypt(msg['body'].encode())
        
        return(msg)


class MessageHandler:




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
        message_dict['gmail_id'] = msg_id
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

    
    service = Service()             # instantiate service
    # get latest n message ids
    #latest_ids = service.retrieve_ids(user_id='me', n=args.n)
    # looks like 500 is the max
    latest_ids = service.retrieve_ids(user_id='me', n=800)
    
    # make sure credentials were loaded correctly
    if service == 0:
        return()

    # instantiate cryptography handler
    crypt_handler = CryptHandler()

    # get the secret key
    key = crypt_handler.get_key()
    
    # instantiate the fernet
    f = Fernet(key)

    # instantiate message handler
    handler = MessageHandler()
   


    # instantiate list of messages
    retrieved_messages = []

    # loop over messages and append to retrieved_messages list
    # also encrypt the dict values here
    for id in latest_ids:
        msg = handler.get_message_content(service, 'me', id)
        if args.e:
            msg = crypt_handler.encrypt_message(key=key, msg=msg, fernet=f)

        # write to db?
        handler.write_to_db(msg=msg, encrypt=args.e)

        retrieved_messages.append(msg)

     
    # for i in range(0, len(retrieved_messages)):
    #     for j in retrieved_messages[i].keys():
    #         if j == 'gmail_id':
    #             j = f.encrypt(retrieved_messages[i])

    # test = retrieved_messages[0].values

    # token = f.encrypt(retrieved_messages[0]['from'].encode())
    # #f.decrypt(token)

    # write to json filee
    #j = json.dumps(retrieved_messages, indent=4)
    #f = open('sample2.json', 'w')
    #print(j, file = f)
    #f.close()

if __name__ == '__main__':
    main()





