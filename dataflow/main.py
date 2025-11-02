import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions
from utils.transforms import process_event, filter_null
import google.auth

# Detecta o project a partir do ambiente IAM (Dataflow SA)
credentials, PROJECT_ID = google.auth.default()

SUBSCRIPTION = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"

BQ_PURCHASE = f"{PROJECT_ID}:streaming.staging_purchase"
BQ_CANCEL = f"{PROJECT_ID}:streaming.staging_cancellation"


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
        
        events = (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "ParseJSON" >> beam.Map(json.loads)
            | "FilterNull" >> beam.Filter(filter_null)
            | "ProcessEvent" >> beam.Map(process_event)
            | "FilterValid" >> beam.Filter(lambda e: e is not None)
        )

        purchases = events | "FilterPurchases" >> beam.Filter(lambda e: e["destination"] == "buy")
        cancels = events | "FilterCancellations" >> beam.Filter(lambda e: e["destination"] == "cancellation")

        purchases | "WritePurchasesBQ" >> beam.io.WriteToBigQuery(
            table=BQ_PURCHASE,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            custom_gcs_temp_location=f"gs://cars-sales-{PROJECT_ID}-prod-dataflow-temp/temp"
        )

        cancels | "WriteCancellationsBQ" >> beam.io.WriteToBigQuery(
            table=BQ_CANCEL,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            custom_gcs_temp_location=f"gs://cars-sales-{PROJECT_ID}-prod-dataflow-temp/temp"
        )


if __name__ == "__main__":
    run()
