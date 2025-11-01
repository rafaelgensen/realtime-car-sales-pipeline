provider "google" {
  project = var.project_id
  region  = var.region
}

# Módulo para Pub/Sub
module "pubsub" {
  source     = "./modules/pubsub"
  project_id = var.project_id
  env        = var.env
  region     = var.region
}

# Módulo para GCS
module "gcs" {
  source     = "./modules/gcs"
  project_id = var.project_id
  env        = var.env
  region     = var.region
}

# Módulo para IAM do Dataflow
module "dataflow_iam" {
  source         = "./modules/dataflow/iam"
  project_id     = var.project_id
  env            = var.env
  region         = var.region

  depends_on = [
    module.pubsub,
    module.gcs
  ]
}

# Módulo para Job do Dataflow
module "dataflow_jobs" {
  source         = "./modules/dataflow/jobs"
  project_id     = var.project_id
  input_topic    = module.pubsub.events_topic
  temp_location  = module.gcs.temp_location
  env            = var.env

  depends_on = [
    module.dataflow_iam
  ]
}