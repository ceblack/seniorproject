#!/usr/bin/env python3
import json
import time
from datetime import datetime

def get_timestamp():
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    utc_offset = offset / 60 / 60 * -1
    timezone = time.tzname[time.daylight]
    return(ts,utc_offset,timezone)

if __name__ == "__main__":
    print(get_timestamp())
