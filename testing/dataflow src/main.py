import argparse
import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseMessage(beam.DoFn):
    def process(self, element):
        record = json.loads(element)
        yield {
            "event_id": record.get("event_id"),
            "user_id": record.get("user_id"),
            "event_type": record.get("event_type"),
            "timestamp": record.get("timestamp"),
        }

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_topic")
    parser.add_argument("--output_table")
    parser.add_argument("--temp_location")
    args, beam_args = parser.parse_known_args(argv)

    options = PipelineOptions(beam_args, save_main_session=True, streaming=True)

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=args.input_topic)
            | "ParseJSON" >> beam.ParDo(ParseMessage())
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                args.output_table,
                schema="event_id:STRING,user_id:STRING,event_type:STRING,timestamp:TIMESTAMP",
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            )
        )

if __name__ == "__main__":
    run()
