import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

PROJECT_ID = "vaulted-acolyte-462921-v2"
INPUT_SUB = f"projects/{PROJECT_ID}/subscriptions/cars-sales-{PROJECT_ID}-prod-events-sub"
OUTPUT_PATH = f"gs://cars-sales-{PROJECT_ID}-prod-events-staging/events/output"

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
            accumulation_mode=beam.trigger.AccumulationMode.DISCARDING,
        )

        (
            windowed
            | "ToJson" >> beam.Map(json.dumps)
            | "Write" >> beam.io.WriteToText(
                file_path_prefix=OUTPUT_PATH,
                file_name_suffix=".json",
                num_shards=5,
                # chave: habilita escrita para coleções não delimitadas com janelas
                windowed_writes=True,
            )
        )

if __name__ == "__main__":
    run()
