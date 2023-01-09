import datetime, pytz


def get_time():
    return datetime.datetime.now(tz=pytz.timezone('Europe/Berlin'))
