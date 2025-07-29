from datetime import datetime
import pytz


def get_utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def convert_to_utc(dt, tz_str):
    tz = pytz.timezone(tz_str)
    return tz.localize(dt).astimezone(pytz.utc)


def get_time_in_tz(utc_dt, tz_str):
    tz = pytz.timezone(tz_str)
    return utc_dt.astimezone(tz)


def get_all_timezones():
    return pytz.all_timezones
