import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from google.cloud import storage
import google.auth


def load_config_from_gcs():
    """Lê o JSON de configuração do bucket Terraform."""
    # Descobre o projeto e as credenciais atuais
    credentials, project_id = google.auth.default()

    # Bucket criado via Terraform (mesmo nome usado no resource)
    bucket_name = f"cars-sales-{project_id}-prod-dataflow-temp"
    blob_name = "config/input_output_config.json"

    client = storage.Client(credentials=credentials, project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    content = blob.download_as_text()

    return json.loads(content), project_id


def run():
    config, project_id = load_config_from_gcs()

    region = "us-central1"  # fixo, pode alterar aqui se quiser
    input_subscription = f"projects/{project_id}/subscriptions/{config['input_topic']}"
    output_bucket = config["output_bucket"]

    options = PipelineOptions(
        project=project_id,
        region=region,
        temp_location=f"gs://cars-sales-{project_id}-prod-dataflow-temp/temp/",
        runner="DataflowRunner",
        streaming=True,
    )

    with beam.Pipeline(options=options) as p:
        events = (
            p
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Decode UTF-8" >> beam.Map(lambda x: x.decode("utf-8"))
            | "Parse JSON" >> beam.Map(json.loads)
        )

        filtered = events | "Filter nulls" >> beam.Filter(lambda e: e is not None and e != "")

        processed = (
            filtered
            | "Process event" >> beam.Map(process_event)
            | "Filter invalid" >> beam.Filter(lambda e: e is not None)
        )

        (
            processed
            | "Write to GCS" >> beam.io.WriteToText(
                f"gs://{output_bucket}/events",
                file_name_suffix=".json",
                shard_name_template="-SSSSS-of-NNNNN"
            )
        )


if __name__ == "__main__":
    from utils.transforms import filter_null, process_event, write_to_gcs
    run()