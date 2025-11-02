import apache_beam as beam
from datetime import datetime

def parse_ts(ts):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt).isoformat()
        except ValueError:
            pass
    return None

def filter_null(event):
    if not event or "type" not in event or "timestamp" not in event:
        return False
    return True

def process_event(event):
    ts = parse_ts(event["timestamp"])
    if not ts:
        return None
    
    event["timestamp"] = ts

    if event["type"] == "purchase":
        event["destination"] = "buy"
    elif event["type"] == "cancellation":
        event["destination"] = "cancellation"
    else:
        return None
    
    return event
