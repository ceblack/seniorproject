#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import json
from morningstar.json_toolkit import timestamp

def format_json(status, error, payload):
    try:
        ts, utc_offset, timezone = timestamp.get_timestamp()
        jstring = {"status":status, "timestamp":str(ts), "utc_offset":str(utc_offset), "timezone":timezone, "error":error, "payload":payload}
        jdata = json.dumps(jstring)
        return(jdata)
    except Exception as e:
        jstring = {"status":"failure", "timestamp":"", "utc_offset":"", "timezone":"", "error":str(e), "payload":[]}
        jdata = json.dumps(jstring)
        return(jdata)
