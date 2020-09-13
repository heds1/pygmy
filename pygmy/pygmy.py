from bs4 import BeautifulSoup
import base64
from cryptography.fernet import Fernet
import sqlite3
import os
#from __future__ import print_function
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import email

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class Message:
    # instantiate a Message object with just the Gmail ID
    def __init__(self, id):
        self.gmail_id = id
        self.thread = None
        self.date = None
        self.sender_name = None
        self.sender_email = None
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

    
    def parse_thread(self, message):
        try:
            self.thread = message['threadId']
        except:
            print('Error in parse_thread.')


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
        import re
        """
        Parse the metadata of a returned message JSON object,
        using the intermediate message headers. saves to Message object.
        param id:
            the gmail_id of the message
        param headers:
            the returned objects of Message.parse_headers().
        return: 
            none
        """
        try:
            self.date = headers['Date']
            _name = re.search(r"(.*?)(?= \<)", headers['From'])
            if _name is not None:
                self.sender_name = _name.group(0)
            _email = re.search(r"(?<=\<).*?(?=\>)", headers['From'])
            if _email is not None:
                self.sender_email = _email.group(0)
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
                    print('Error in Message.parse_body() - unsupported MIME type.')
        
        # otherwise, we have a different type of message -- should be able
        # to access 'body' directly
        elif 'body' in payload.keys():
            message_body = payload['body']['data']
            message_type = payload['mimeType']

        else:
            print('Error in Message.parse_body().')
        
        self.body = self.decode(message_body)
        self.type = message_type
        return


    def retrieve_attachment_ids(self, payload):
        """
        check for any attachments. if any are found,
        return dict of attachment ids, where key is the
        attachmentId as a string, and value is the filename
        of the given attachmentId. 
        payload is given by payload['payload'],
        i.e., the same payload passed to parse_body.
        """
        attachment_ids = {}
        if 'parts' in payload.keys():
            for i in payload['parts']:
                if 'attachmentId' in i['body'].keys():
                    attachment_ids[i['body']['attachmentId']] = i['filename']
            return attachment_ids

        else:
            return


    def retrieve_attachment(self, service, user_id, attachment_id):
        """
        retrieve an attachment from a given attachment id. attachment_id
        is the key of an element of the attachment_ids dictionary produced
        by Message.retrieve_attachment_ids.
        """
        try:
            attachment = service.users().messages().attachments().get(
                userId=user_id, messageId=self.gmail_id, id=attachment_id).execute()
            return attachment['data']
        except:
            print('Error in Message.retrieve_attachment()')
            return None


    # def save_attachment(self, filename, data):
    #     """
    #     decodes and saves an attachment to the filesystem. 
    #     attachments are encoded in base64.
    #     filename and data arguments are provided by the key and value,
    #     respectively, of an element of the attachment_ids dictionary.
    #     """
    #     print('pretending to save attachment')
    #     with open(filename, 'wb') as f:
    #         f.write(base64.urlsafe_b64decode(data))

    def write_attachment(self, conn, attachment_id, filename, data):
        """
        writes attachment to database.
        """
        print('saving attachment ' + filename + ' to database...')
        c = conn.cursor()
        t = (self.gmail_id,
            attachment_id,
            filename,
            data)
        c.execute("""INSERT INTO attachments
            (gmail_id, attachment_id, filename, data)
            VALUES (?,?,?,?)""", t)
        conn.commit()


    # attachment = service.users().messages().get(userId=user_id, id=self.gmail_id).execute()
    # def write_to_json(self):
    #     j = json.dumps(self.__dict__, indent=4)
    #     f = open('sample.json', 'a')
    #     print(j, file = f)
    #     f.close()


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


    def write_to_db(self, conn):
        c = conn.cursor()
        t = (self.gmail_id,
            self.thread,
            self.sender_email,
            self.sender_name,
            self.date,
            self.subject,
            self.body)
        c.execute("""INSERT INTO messages
            (gmail_id, thread, sender_email, sender_name, date, subject, body)
            VALUES (?,?,?,?,?,?,?)""", t)
        conn.commit()


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


class DatabaseHandler:
    """
    connects to an existing database.
    instantiated with a database file.
    if no database file is found,
    creates a new database.
    """
    def __init__(self, database):
        try:
            conn = sqlite3.connect(database)
        except sqlite3.Error as e:
            print('DatabaseHandler error: ' + e)
        finally:
            self.conn = conn

        # create table if it doesn't exist
        try:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id integer PRIMARY KEY,
                    gmail_id text NOT NULL UNIQUE,
                    thread text,
                    sender_email text,
                    sender_name text,
                    date text,
                    subject text,
                    body text
                );"""
            )
            c.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id integer PRIMARY KEY,
                    gmail_id text NOT NULL,
                    attachment_id text NOT NULL,
                    filename text NOT NULL,
                    data text NOT NULL
                );"""
            )
        except sqlite3.Error as e:
            print('DatabaseHandler error: ' + e)


    def get_ids(self):
        try:
            c = self.conn.cursor()
            ids = []
            for row in c.execute("""SELECT gmail_id FROM messages;"""):
                # a tuple of len 1 is returned, just get the only element
                ids.append(row[0])
        except sqlite3.Error as e:
            print('DatabaseHandler.get_ids() error: ' + e)
        return ids

    
    def close(self):
        self.conn.close()