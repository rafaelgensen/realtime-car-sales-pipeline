import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

def process_event(e):
    # mantém tua lógica se tiver, aqui só passthrough
    return e

def run():
    # hardcode total para teste
    project_id = "vaulted-acolyte-462921-v2"
    input_subscription = "projects/vaulted-acolyte-462921-v2/subscriptions/cars-sales-vaulted-acolyte-462921-v2-prod-events-sub"
    output_bucket = "cars-sales-vaulted-acolyte-462921-v2-prod-events-staging"

    options = PipelineOptions(
        project=project_id,
        region="us-central1",
        temp_location=f"gs://cars-sales-{project_id}-prod-dataflow-temp/temp",
        runner="DataflowRunner",
        streaming=True,
    )
    options.view_as(StandardOptions).streaming = True
    options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=options) as p:
        events = (
            p
            | "Read" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse" >> beam.Map(json.loads)
            | "Process" >> beam.Map(process_event)
            | "FilterNone" >> beam.Filter(lambda e: e is not None)
        )

        windowed = events | beam.WindowInto(
            beam.window.FixedWindows(5),
            trigger=beam.trigger.AfterProcessingTime(2),
            accumulation_mode=beam.trigger.AccumulationMode.DISCARDING
        )

        (
            windowed
            | "ToJson" >> beam.Map(json.dumps)
            | "Write" >> beam.io.WriteToText(
                file_path_prefix=f"gs://{output_bucket}/events/output",
                file_name_suffix=".json",
                num_shards=1
            )
        )

if __name__ == "__main__":
    run()
