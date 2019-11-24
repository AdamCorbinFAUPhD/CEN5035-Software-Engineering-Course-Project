import datetime

import pytz as pytz

date_time_str = '2018-06-29 08:15:27.243860'
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
print(date_time_obj)
'%Y-%m-%d %H:%M:%S.%f'
data = "2019-11-11T06:00:00-05:00"
# result2 = datetime.datetime.strptime(data[0:23], "%Y-%m-%dT%H:%M:%S")
org_dt = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
start_dt = (datetime.datetime.fromisoformat(data) - org_dt).total_seconds()


def should_system_be_armed(event_start_str, event_event_str):
    """
    This function will convert the start and end string iso times, to date times. The it will check to see if current
    falls between the start and end times. If so True will be returned, otherwise False will be returned

    :param event_start_str:
    :param event_event_str:
    :return:
    """
    org_dt = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
    start_time_in_sec = (datetime.datetime.fromisoformat(event_start_str) - org_dt).total_seconds()
    end_time_in_sec = (datetime.datetime.fromisoformat(event_event_str) - org_dt).total_seconds()
    current_time_in_sec = (datetime.now() - org_dt).total_seconds()

    return True if start_time_in_sec < end_time_in_sec < current_time_in_sec else False


print(start_dt)
# print(result2)
