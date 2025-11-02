import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

PROJECT_ID = "vaulted-acolyte-462921-v2"
SUBSCRIPTION = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
BQ_TABLE = f"{PROJECT_ID}:streaming.raw_events"

def run():
    options = PipelineOptions(
        project=PROJECT_ID,
        region="us-central1",
        runner="DataflowRunner",
        temp_location=f"gs://cars-sales-{PROJECT_ID}-prod-dataflow-temp/temp",
        streaming=True,
    )
    options.view_as(StandardOptions).streaming = True
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Wrap" >> beam.Map(lambda m: {"payload": m})
            | "WriteBQ" >> beam.io.WriteToBigQuery(
                table=BQ_TABLE,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            )
        )

if __name__ == "__main__":
    run()