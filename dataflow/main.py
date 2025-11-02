import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

PROJECT_ID = "vaulted-acolyte-462921-v2"
INPUT_SUB = "projects/vaulted-acolyte-462921-v2/subscriptions/cars-sales-vaulted-acolyte-462921-v2-prod-events-sub"
OUTPUT_PATH = "gs://cars-sales-vaulted-acolyte-462921-v2-prod-events-staging/events/output"

class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument("--mode", default="run")

def run():
    options = PipelineOptions(
        project=PROJECT_ID,
        region="us-central1",
        temp_location="gs://cars-sales-vaulted-acolyte-462921-v2-prod-dataflow-temp/temp",
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
            | "Filter" >> beam.Filter(lambda e: e is not None)
        )

        windowed = events | "Window" >> beam.WindowInto(
            beam.window.FixedWindows(10),
            trigger=beam.trigger.AfterProcessingTime(5),
            accumulation_mode=beam.trigger.AccumulationMode.DISCARDING,
        )

        def is_template():
            try:
                return custom.mode.get() == "template"
            except:
                return False  # during template build

        if is_template():
            _ = windowed | "NoOp" >> beam.Map(lambda _: None)
        else:
            (
                windowed
                | "ToJson" >> beam.Map(json.dumps)
                | "Write" >> beam.io.WriteToText(
                    file_path_prefix=OUTPUT_PATH,
                    file_name_suffix=".json",
                    num_shards=5
                )
            )

if __name__ == "__main__":
    run()
