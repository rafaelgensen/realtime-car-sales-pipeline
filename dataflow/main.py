import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.options.value_provider import RuntimeValueProvider
from google.cloud import storage
import google.auth

# --------------------
# Custom flag
# --------------------
class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            "--template_mode",
            default=False,  # key: default runtime = writes to GCS
            type=bool,
            help="True only when generating Dataflow template"
        )

# --------------------
# Config loader
# --------------------
def load_config_from_gcs():
    credentials, project_id = google.auth.default()
    bucket_name = f"cars-sales-{project_id}-prod-dataflow-temp"
    blob_name = "config/input_output_config.json"
    client = storage.Client(credentials=credentials, project=project_id)
    content = client.bucket(bucket_name).blob(blob_name).download_as_text()
    return json.loads(content), project_id

# --------------------
# Pipeline
# --------------------
def run():
    from utils.transforms import process_event  # ensure packaged

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

        processed = (
            events
            | "Process event" >> beam.Map(process_event)
            | "Filter valid" >> beam.Filter(lambda e: e is not None)
        )

        windowed = (
            processed
            | "Window10s" >> beam.WindowInto(
                beam.window.FixedWindows(10),
                trigger=beam.trigger.AfterProcessingTime(5),
                accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
            )
        )

        # --------------------
        # RUNTIME output (template_mode = false)
        # --------------------
        runtime_branch = (
            windowed
            | "To JSON string" >> beam.Map(json.dumps)
        )

        # Runtime write branch guarded by template flag
        (
            runtime_branch
            | "Write To GCS" >> beam.io.WriteToText(
                file_path_prefix=f"gs://{output_bucket}/events/output",
                file_name_suffix=".json",
                num_shards=3
            )
        ).only_if(custom.template_mode == False)

        # --------------------
        # TEMPLATE build branch (no output)
        # --------------------
        (
            windowed
            | "No-op for template" >> beam.FlatMap(lambda _: [])
        ).only_if(custom.template_mode == True)

# --------------------
# Entry
# --------------------
if __name__ == "__main__":
    run()
