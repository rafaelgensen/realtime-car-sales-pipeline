import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from google.cloud import storage
import google.auth


def load_config_from_gcs():
    credentials, project_id = google.auth.default()
    bucket_name = f"cars-sales-{project_id}-prod-dataflow-temp"
    blob_name = "config/input_output_config.json"
    client = storage.Client(credentials=credentials, project=project_id)
    content = client.bucket(bucket_name).blob(blob_name).download_as_text()
    return json.loads(content), project_id


def run():
    config, project_id = load_config_from_gcs()

    input_subscription = f"projects/{project_id}/subscriptions/{config['input_topic']}"
    output_bucket = config["output_bucket"]

    options = PipelineOptions(
        project=project_id,
        region="us-central1",
        temp_location=f"gs://cars-sales-{project_id}-prod-dataflow-temp/temp/",
        runner="DataflowRunner",
        streaming=True,
    )
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        events = (
            p
            | "Read PubSub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse JSON" >> beam.Map(json.loads)
        )

        filtered = events | "Filter nulls" >> beam.Filter(lambda e: e)

        processed = (
            filtered
            | "Process event" >> beam.Map(process_event)
            | "Filter invalid" >> beam.Filter(lambda e: e is not None)
        )

        windowed = (
            processed
            | "Window10s" >> beam.WindowInto(
                beam.window.FixedWindows(10),
                trigger=beam.trigger.AfterProcessingTime(5),
                accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
            )
        )

        _ = (
            windowed
            | "ToStr" >> beam.Map(lambda e: json.dumps(e))
            | "Write" >> beam.io.fileio.WriteToFiles(
                path=f"gs://{output_bucket}/events/",
                file_naming=beam.io.fileio.destination_prefix_naming("part"),
                destination=lambda x: "",  # single destination
                max_records_per_file=2000  # ~streaming friendly
            )
        )


if __name__ == "__main__":
    from utils.transforms import filter_null, process_event, write_to_gcs
    run()
