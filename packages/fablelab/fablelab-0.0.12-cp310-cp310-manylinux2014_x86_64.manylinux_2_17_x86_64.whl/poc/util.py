import pytz
from datetime import datetime, timedelta

_korean_tz = pytz.timezone('Asia/Seoul')

def datetime_sub(days=0):
    return datetime.now(_korean_tz) - timedelta(days=days)

def format_yesterday(format='%Y%m%d'):
    return datetime_sub(1).strftime(format)