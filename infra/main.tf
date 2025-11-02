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
module "bq" {
  source     = "./modules/bigquery"
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
    module.pubsub
  ]
}

# Módulo para Job do Dataflow
module "dataflow_jobs" {
  source         = "./modules/dataflow/job"
  project_id     = var.project_id
  env            = var.env
  region         = var.region

  depends_on = [
    module.dataflow_iam
  ]
}