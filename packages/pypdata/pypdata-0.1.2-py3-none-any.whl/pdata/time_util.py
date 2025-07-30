import datetime


__all__ = [
    'EPOCH_START',
    'LOCAL_TIME_OFFSET',
    'utc_timestamp'
]


EPOCH_START = datetime.datetime(1970, 1, 1)
LOCAL_TIME_OFFSET = int(datetime.datetime.now(datetime.timezone.utc).astimezone().utcoffset().total_seconds() * 1000)


def utc_timestamp(dt: datetime.date | datetime.datetime):
    if isinstance(dt, datetime.date):
        dt = datetime.datetime.combine(dt, datetime.time.min)
    return int((dt - EPOCH_START).total_seconds() * 1000)
