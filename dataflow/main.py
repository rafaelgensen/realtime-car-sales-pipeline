import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from google.cloud import storage
import google.auth
import sys

# --- CONFIG LOAD ---
def load_config_from_gcs():
    credentials, project_id = google.auth.default()
    bucket_name = f"cars-sales-{project_id}-prod-dataflow-temp"
    blob_name = "config/input_output_config.json"
    client = storage.Client(credentials=credentials, project=project_id)
    content = client.bucket(bucket_name).blob(blob_name).download_as_text()
    return json.loads(content), project_id

# --- PARSING ---
def parse_ts(event):
    from datetime import datetime
    ts = event.get("timestamp")
    try:
        event["timestamp"] = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        event["timestamp"] = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    return event

def process_event(event):
    t = event.get("type")
    if t == "purchase":
        event["destination"] = "buy"
    elif t == "cancellation":
        event["destination"] = "cancellation"
    else:
        return None
    return event

# --- PIPELINE ---
def run():
    config, project_id = load_config_from_gcs()
    input_subscription = f"projects/{project_id}/subscriptions/{config['input_topic']}"
    output_bucket = config["output_bucket"]

    opts = PipelineOptions(
        project=project_id,
        region="us-central1",
        temp_location=f"gs://cars-sales-{project_id}-prod-dataflow-temp/temp/",
        runner="DataflowRunner",
        streaming=True,
    )
    opts.view_as(StandardOptions).streaming = True

    # detect template build mode
    is_template_build = "--template" in sys.argv

    with beam.Pipeline(options=opts) as p:
        events = (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "ParseJSON" >> beam.Map(json.loads)
            | "DropNull" >> beam.Filter(lambda e: e)
            | "ParseTS" >> beam.Map(parse_ts)
            | "Process" >> beam.Map(process_event)
            | "DropInvalid" >> beam.Filter(lambda e: e is not None)
            | "Window" >> beam.WindowInto(
                beam.window.FixedWindows(10),
                trigger=beam.trigger.AfterProcessingTime(5),
                accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
            )
        )

        if not is_template_build:
            (
                events
                | "ToStr" >> beam.Map(json.dumps)
                | "Write" >> beam.io.WriteToText(
                    file_path_prefix=f"gs://{output_bucket}/events/output",
                    file_name_suffix=".json",
                    num_shards=5
                )
            )
        else:
            _ = events | "Noop" >> beam.Map(lambda x: None)

if __name__ == "__main__":
    from utils.transforms import filter_null, process_event, write_to_gcs
    run()
