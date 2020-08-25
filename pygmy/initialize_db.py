sqlite3

CREATE TABLE EMAILS(
    ID int primary key,
    Sender varchar(100),
    Date varchar(100),
    Subject varchar(100),
    Content varchar
);

message = {
    'from': 'sender@gmail.com',
    'date': '2020-01-01',
    'subject': 'Cool Subject',
    'data': 'content'
}   

INSERT INTO EMAILS(Sender, Date, Subject, Content)
VALUES(message['from'], message['date'], message['subject'], message['data'])



