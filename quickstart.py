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

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    
    #testmsg = service.users().messages().get(userId='me',id='173d231536a300b5', format='full').execute()

    # testmsg obj is a dict of a single email now
    # examine with keys(), e.g., 
    # testmsg.keys()
    # most of the interesting stuff is in payload, e.g.,
    # testmsg['payload'].keys()
    # then go into the headers for essentially metadata. this is a list, e.g.,
    # type(testmsg['payload']['headers'])
    # looks like a list of dicts actually.

    # loop over the list to get the 'name' keys?
    # my_headers = testmsg['payload']['headers']
    # for i in my_headers:
        # if i['name'] == 'From':
        #     print('From: ' + i['value'])
        # if i['name'] == 'Date':
        #     print('Date: ' + i['value'])
        # if i['name'] == 'Subject':
        #     print('Subject: ' + i['value'])

    # then go into body for the actual message.
    # actually no not in this case.

    # lets try to list the messages now
    # allm = service.users().messages().list(userId='me').execute()

    # what do we have
    # for i in allm:
    #     print(i)
    # messages
    # nextPageToken
    # resultSizeEstimate
    # len(allm['messages']) # returns 100, default limit?

    # looks like this just contains id and threadId:
    # testmsg2 = allm['messages'][1]

    # and we're supposed to use messages.get() to actually get the message.
    # we can set maxResults
    fivemsgs = service.users().messages().list(userId='me', maxResults=5).execute()

    # lets try to get each of these messages
retrieved_msgs = []
for i in fivemsgs['messages']:
    this_msg = service.users().messages().get(userId='me', id=i['id'], format='full').execute()
    my_headers = this_msg['payload']['headers']
    for h in my_headers:
        if h['name'] == 'From':
            print('From: ' + h['value'])
        if h['name'] == 'Date':
            print('Date: ' + h['value'])
        if h['name'] == 'Subject':
            print('Subject: ' + h['value'])
    
id='173b864997b95d2c'
message = service.users().messages().get(userId='me', id=id).execute()
# i don't know why and can't find any documentation for this stupid fucking
# thing, but you don't go via payload/body, you go via payload/parts
msg_det = message['payload']['parts']
for i in msg_det:
    print(i)



# Fetching message body
mssg_parts = msg_det = message['payload']['parts'] # fetching the message parts
part_one  = mssg_parts[0] # fetching first element of the part 
part_body = part_one['body'] # fetching body of the message
part_data = part_body['data'] # fetching data from the body
clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
soup = BeautifulSoup(clean_two , "lxml" )
mssg_body = soup.body()
# mssg_body is a readible form of message body
# depending on the end user's requirements, it can be further cleaned 
# using regex, beautiful soup, or any other method
temp_dict['Message_body'] = mssg_body

    retrieved_msgs.append(this_msg)
    print(i['id'])

    print('aye')

    # todo download conditionally on unread/read (label??)

    # alright we have five msgs downloaded in full
for i in retrieved_msgs:
    print(i['headers'])


if __name__ == '__main__':
    main()
