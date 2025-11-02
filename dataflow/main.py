import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

PROJECT_ID = "vaulted-acolyte-462921-v2"
SUBSCRIPTION = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
OUTPUT_PREFIX = f"gs://cars-sales-{PROJECT_ID}-prod-events-staging/events/output"

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
            # janela simples de 60s para permitir write em streaming
            | "Window60s" >> beam.WindowInto(beam.window.FixedWindows(60))
            | "WriteGCS" >> beam.io.WriteToText(
                file_path_prefix=OUTPUT_PREFIX,
                file_name_suffix=".json",
                num_shards=1
            )
        )

if __name__ == "__main__":
    run()
