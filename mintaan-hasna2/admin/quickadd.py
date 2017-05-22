import argparse
import httplib2
import os
from googleapiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

def main():
    credential_path = os.path.join(os.getcwd(), email + '.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    listCal = service.calendarList().list().execute()['items']
    for cal in listCal:
        print cal['summary']

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'calendar.json'
APPLICATION_NAME = 'Penjadwalan Seminar/Sidang'

email = raw_input('Masukkan email: ')
if ((email is not None) and (email != '')):
    main()
else:
    print 'Email tidak valid.'