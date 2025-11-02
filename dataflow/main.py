import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.options.value_provider import RuntimeValueProvider
from google.cloud import storage
import google.auth

from utils.transforms import process_event


class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            "--template_mode",
            default=False,
            type=bool,
            help="True when building template"
        )


def load_config():
    credentials, project_id = google.auth.default()
    bucket = f"cars-sales-{project_id}-prod-dataflow-temp"
    blob = "config/input_output_config.json"
    client = storage.Client(credentials=credentials, project=project_id)
    data = client.bucket(bucket).blob(blob).download_as_text()
    return json.loads(data), project_id


def run():
    config, project_id = load_config()

    input_sub = f"projects/{project_id}/subscriptions/{config['input_topic']}"
    output_bucket = config["output_bucket"]

    opts = PipelineOptions(
        project=project_id,
        region="us-central1",
        temp_location=f"gs://cars-sales-{project_id}-prod-dataflow-temp/temp/",
        runner="DataflowRunner",
        streaming=True,
    )
    opts.view_as(StandardOptions).streaming = True
    custom = opts.view_as(CustomOptions)

    with beam.Pipeline(options=opts) as p:

        events = (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=input_sub)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse" >> beam.Map(json.loads)
            | "Process" >> beam.Map(process_event)
            | "Filter valid" >> beam.Filter(lambda e: e is not None)
            | "Window10s" >> beam.WindowInto(
                beam.window.FixedWindows(10),
                trigger=beam.trigger.AfterProcessingTime(5),
                accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
            )
        )

        # Runtime: write
        (
            events
            | "WriteToGCS"
            >> beam.io.WriteToText(
                file_path_prefix=f"gs://{output_bucket}/events/output",
                file_name_suffix=".json",
                num_shards=1,
            )
            .only_if(custom.template_mode == False)
        )

        # Template build: no-op
        (
            events
            | "TemplateNoOp"
            >> beam.FlatMap(lambda x: [])
            .only_if(custom.template_mode == True)
        )


if __name__ == "__main__":
    run()
