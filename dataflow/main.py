import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam import window
import json

PROJECT_ID = "vaulted-acolyte-462921-v2"
SUB = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
OUT = f"gs://cars-sales-{PROJECT_ID}-prod-events-staging/events/output"

def run():
    opts = PipelineOptions(
        project=PROJECT_ID,
        region="us-central1",
        runner="DataflowRunner",
        temp_location=f"gs://cars-sales-{PROJECT_ID}-prod-dataflow-temp/temp",
        streaming=True
    )
    opts.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=opts) as p:
        (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=SUB)
            | "Decode" >> beam.Map(lambda b: b.decode("utf-8"))
            | "ParseJSON" >> beam.Map(lambda x: json.loads(x))
            | "Window5s" >> beam.WindowInto(window.FixedWindows(5))
            | "ToString" >> beam.Map(lambda x: json.dumps(x))
            | "Write" >> beam.io.WriteToText(
                file_path_prefix=OUT,
                file_name_suffix=".json",
                num_shards=1
            )
        )

if __name__ == "__main__":
    run()