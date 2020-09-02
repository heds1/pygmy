import argparse
import pygmy
    
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
    service = pygmy.Service()       
    
    # instantiate cryptography handler
    if args.e:
        encryptor = pygmy.Encryptor()

    # connect to database
    db = pygmy.DatabaseHandler(database='db.sqlite')

    # get latest n message ids; compare against stored ids
    latest_ids = service.retrieve_ids(user_id='me', n=args.n)
    stored_ids = db.get_ids()
    new_ids = set(latest_ids).difference(stored_ids)
    print('Of the ' + str(len(latest_ids)) + ' latest messages queried, ' + str(len(new_ids)) + ' new messages were downloaded.')

    # retrieve and save messages that are not already retrieved
    for id in new_ids:
        message = pygmy.Message(id)
        payload = message.retrieve_message(service.service, 'me')
        headers = message.parse_headers(payload)
        message.parse_thread(payload)
        message.parse_metadata(headers)
        message.parse_body(payload['payload'])

        if args.e:
            message.body = encryptor.encrypt(message.body)

        # write to the database
        message.write_to_db(conn = db.conn)

    # close connection
    db.close()
    

if __name__ == '__main__':
    main()


        



