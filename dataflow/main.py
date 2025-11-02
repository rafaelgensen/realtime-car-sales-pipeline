import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions
from apache_beam.io import fileio

PROJECT_ID = "vaulted-acolyte-462921-v2"
INPUT_SUB = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
OUTPUT_BUCKET = f"cars-sales-{PROJECT_ID}-prod-events-staging"

class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            "--mode",
            type=str,
            default="run",
            help="template or run"
        )

def run():
    options = PipelineOptions(
        project=PROJECT_ID,
        region="us-central1",
        temp_location=f"gs://cars-sales-{PROJECT_ID}-prod-dataflow-temp/temp",
        runner="DataflowRunner",
        streaming=True,
    )
    options.view_as(StandardOptions).streaming = True
    options.view_as(SetupOptions).save_main_session = True
    custom = options.view_as(CustomOptions)

    from utils.transforms import process_event

    with beam.Pipeline(options=options) as p:
        events = (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=INPUT_SUB)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse" >> beam.Map(json.loads)
            | "Process" >> beam.Map(process_event)
            | "FilterNone" >> beam.Filter(lambda e: e is not None)
        )

        windowed = events | "Window" >> beam.WindowInto(
            beam.window.FixedWindows(10),
            trigger=beam.trigger.AfterProcessingTime(5),
            accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
        )

        def is_template():
            return custom.mode.is_accessible() and custom.mode.get() == "template"

        if is_template():
            _ = windowed | "NoOp" >> beam.Map(lambda _: None)
        else:
            (
                windowed
                | "ToJson" >> beam.Map(json.dumps)
                | "PairWithKey" >> beam.Map(lambda x: ("", x))
                | "WriteFiles" >> fileio.WriteToFiles(
                    path=f"gs://{OUTPUT_BUCKET}/events/",
                    file_naming=fileio.FileNaming.prefix_suffix("output", ".json"),
                    sink=lambda dest: fileio.TextSink()
                )
            )

if __name__ == "__main__":
    run()