provider "google" {
  project = var.project_id
  region  = var.region
}

#module "pubsub" {
#  source     = "./modules/pubsub"
#  project_id = var.project_id
#  env        = var.env
#}

module "gcs" {
  source     = "./modules/gcs"
  project_id = var.project_id
  env        = var.env
}

#module "bigquery" {
#  source     = "./modules/bigquery"
#  project_id = var.project_id
#  env        = var.env
#}

#module "dataflow" {
#  source         = "./modules/dataflow"
#  project_id     = var.project_id
#  env            = var.env
#  input_topic    = module.pubsub.topic_name
#  output_table   = module.bigquery.table_id
#  temp_location  = module.gcs.temp_location
#}