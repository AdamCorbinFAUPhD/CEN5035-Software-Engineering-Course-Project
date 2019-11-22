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
4. First and Last meetings - Automatically create a range where the system will be active the start of the first meeting
till the end of the last meeting. This still has holes since some meetings might take place at the home of the system owner.

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
from datetime import datetime
import pickle
import os.path

import pytz
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class Calendar:
    def __init__(self):
        self._current_event = None
        self._logger = logging.getLogger('AlarmSystem.calendar')
        self._arming_action_taken = False
        self._disarm_action_taken = False
        self._must_disarm = False

    def check_calendar(self):
        """
        Check the google calendar for the next event and determine if the system should be armed.
        :return: returns a tuple containing two bool values. The first is if an action needs to be taken, the second
        is if it is an arming action
        """
        self._get_current_event()
        if self._current_event:
            start = self._current_event['start'].get('dateTime', self._current_event['start'].get('date'))
            end = self._current_event['end'].get('dateTime', self._current_event['end'].get('date'))
            if not self._arming_action_taken and self._should_system_be_armed(start, end):
                self._must_disarm = False
                self._logger.info("Calendar event starting, arming system.")
                self._arming_action_taken = True
                return True, True
            elif not self._disarm_action_taken and self._is_after_event(end):
                self._logger.info("Calendar event ending, disarming system.")
                self._must_disarm = False
                self._disarm_action_taken = True
                self._current_event = None
                return True, False
            elif self._must_disarm:
                self._logger.info("Event was changed before disarm, disarming system")
                self._must_disarm = False
                return True, False
        return False, False

    def _get_current_event(self):
        """
        Get the event with the closest start time and store it in the current event
        """
        # Call the Calendar API
        service = self._get_api_service()
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime').execute()
        event = events_result.get('items', [])
        event = event[0]  # Event returned is an array even though we specify only 1 result. lets convert it to 1 item
        if self._current_event is None or event and self._current_event != event:
            self._logger.info("New calendar event")
            self._logger.info("Start: " + event["start"]["dateTime"])
            self._logger.info("end: " + event["end"]["dateTime"])
            if self._arming_action_taken and not self._disarm_action_taken:
                self._must_disarm = True
            self._current_event = event
            self._arming_action_taken = False
            self._disarm_action_taken = False

    @staticmethod
    def _is_before_event(event_start_str):
        """
        Function for checking if the current time is before the event start time.
        :param event_start_str: The start time of the event
        :return: bool
        """
        org_dt = datetime(1970, 1, 1, tzinfo=pytz.utc)
        start_time_in_sec = (datetime.fromisoformat(event_start_str) - org_dt).total_seconds()
        now = datetime.now()
        now = now.replace(tzinfo=pytz.timezone('US/Eastern'))
        current_time_in_sec = (now - org_dt).total_seconds()
        return True if start_time_in_sec > current_time_in_sec else False

    @staticmethod
    def _is_after_event(event_end_str):
        """
        Function for checking if the current time is past the given event end time.
        :param event_end_str: The end time of the event
        :return: bool
        """
        org_dt = datetime(1970, 1, 1, tzinfo=pytz.utc)
        end_time_in_sec = (datetime.fromisoformat(event_end_str) - org_dt).total_seconds()
        now = datetime.now()
        now = now.replace(tzinfo=pytz.timezone('US/Eastern'))
        current_time_in_sec = (now - org_dt).total_seconds()
        return True if end_time_in_sec < current_time_in_sec else False

    @staticmethod
    def _should_system_be_armed(event_start_str, event_end_str):
        """
        This function will convert the start and end string iso times, to date times. The it will check to see if current
        falls between the start and end times. If so True will be returned, otherwise False will be returned

        :param event_start_str: IOS time that will be converted to seconds
        :param event_end_str: IOS time that will be converted to seconds
        :return:
        """
        org_dt = datetime(1970, 1, 1, tzinfo=pytz.utc)
        start_time_in_sec = (datetime.fromisoformat(event_start_str) - org_dt).total_seconds()
        end_time_in_sec = (datetime.fromisoformat(event_end_str) - org_dt).total_seconds()
        now = datetime.now()
        now = now.replace(tzinfo=pytz.timezone('US/Eastern'))
        current_time_in_sec = (now - org_dt).total_seconds()
        return True if start_time_in_sec < current_time_in_sec < end_time_in_sec else False

    @staticmethod
    def _get_api_service():
        """
        Setup the google api service for use in retrieving the calendars.
        :return:
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
        service = build('calendar', 'v3', credentials=creds)
        return service

