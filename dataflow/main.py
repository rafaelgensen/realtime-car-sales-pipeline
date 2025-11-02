import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

PROJECT_ID = "vaulted-acolyte-462921-v2"

INPUT_SUB = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
OUTPUT_PREFIX = f"gs://cars-sales-{PROJECT_ID}-prod-events-staging/events/output"

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

    from utils.transforms import process_event

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=INPUT_SUB)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse" >> beam.Map(json.loads)
            | "Process" >> beam.Map(process_event)
            | "FilterNone" >> beam.Filter(lambda e: e is not None)
            | "ToJson" >> beam.Map(json.dumps)
            | "Write" >> beam.io.WriteToText(
                file_path_prefix=OUTPUT_PREFIX,
                file_name_suffix=".json",
                num_shards=1
            )
        )

if __name__ == "__main__":
    run()
