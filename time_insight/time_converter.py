from datetime import datetime
import time

def datetime_from_utc_to_local(utc_datetime):
    """
    This function converts UTC datetime to local datetime

    :param utc_datetime: UTC datetime
    :return: Local datetime
    """
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset