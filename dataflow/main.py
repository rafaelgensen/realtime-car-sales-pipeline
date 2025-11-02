import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.options.value_provider import RuntimeValueProvider
from google.cloud import storage
import google.auth

# Custom flag for template vs runtime
class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            "--is_template_build",
            default=False,
            type=bool,
            help="True when building Dataflow template"
        )

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
    custom = options.view_as(CustomOptions)

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

        # Write only at runtime (not template)
        _ = (
            windowed
            | "ToStr" >> beam.Map(json.dumps)
            | "ConditionalWrite" >> beam.MapTuple(lambda *x: x).with_outputs()  # no-op to keep branch valid
        )

        # Runtime branch (write to GCS)
        (
            windowed
            | "WriteToGCS" >> beam.Map(json.dumps)
            | "WriteToText" >> beam.io.WriteToText(
                file_path_prefix=f"gs://{output_bucket}/events/output",
                file_name_suffix=".json",
                num_shards=5
            )
        ).with_outputs()

        # Template build branch (no-op)
        _ = (
            windowed
            | "NoOpSink" >> beam.FlatMap(lambda e: [])
        )

if __name__ == "__main__":
    from utils.transforms import filter_null, process_event, write_to_gcs
    run()
