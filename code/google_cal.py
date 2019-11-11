"""
# Using the Google Calendar as smart enable system
The concept of the Smart Security System would to leverage the use of hte Google Calendar to know when the system should
be monitoring for intruders. The system will periodically monitory for calendar updates. It will also activate and
deactivate the alarm system based on which events are running.

## Determining when to monitor
There can be a few different ways to determine when the alarm system should be activated.
1. Alarm only on during meetings - With little interactions this will make it simple for the system to only be monitoring
when there is a meeting happening. This could be problematic too because its possible that someone might be working from
home and they might have a false positive . A way to combat this will be introduced in the next option
2. Labeled meetings - Adding some keyword to signify if during this meeting the system should be be monitor mode. This
does leave some room for error if someone forgets to tag the meeting that the system should be monitoring.
3. Complete separate alarm events - Another option would be to completely separate the events in their own type of meeting
to signify only for monitoring.

Due to the time constraints we will be using 1, for our purposes to show that we can interact with the Google Calender

## Considerations
Along with the alarm events is possible to connect up with the user's phone GPS to allow for the system to automatically
activate based on the GPS coordinates. Having some kind of range when someone leaves 0.5miles from home then the system
could be activated automatically.



## Connecting to Google Calendar
We start by using this tutorial on how to
1. Enabling the Google Calendar API
2. Installing the python libs using this command 'pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib'

"""

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    service = get_api_service()


    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        print(event)
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def get_api_service():
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
    service = build('calendar', 'v3', credentials=creds)
    return service


if __name__ == '__main__':
    main()