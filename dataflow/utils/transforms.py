import apache_beam as beam
from apache_beam import pvalue
import json
from datetime import datetime

def parse_ts(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass
    raise ValueError(f"timestamp inválido: {ts}")

def filter_null(event):
    if event is None or not event.get('type') or not event.get('timestamp'):
        return False
    return True

def process_event(event):
    event['timestamp'] = parse_ts(event['timestamp'])
    t = event['type']
    if t == 'purchase':
        event['destination'] = 'buy'
    elif t == 'cancellation':
        event['destination'] = 'cancellation'
    else:
        return None
    return event

def write_to_gcs(event, path_prefix):
    if not event:
        return None
    path = f"{path_prefix}/{event['destination']}/{event['timestamp'].strftime('%Y/%m/%d/')}"
    return (path, event)
