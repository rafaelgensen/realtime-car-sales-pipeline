import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions
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
    options.view_as(SetupOptions).save_main_session = True

    from utils.transforms import process_event

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse" >> beam.Map(json.loads)
            | "Process" >> beam.Map(process_event)
            | "FilterValid" >> beam.Filter(lambda e: e is not None)
            | "Window" >> beam.WindowInto(
                beam.window.FixedWindows(10),
                trigger=beam.trigger.AfterProcessingTime(5),
                accumulation_mode=beam.trigger.AccumulationMode.DISCARDING,
            )
            | "ToJson" >> beam.Map(json.dumps)
            | "Write" >> beam.io.WriteToText(
                file_path_prefix=f"gs://{output_bucket}/events/output",
                file_name_suffix=".json",
                num_shards=5,
            )
        )


if __name__ == "__main__":
    run()
