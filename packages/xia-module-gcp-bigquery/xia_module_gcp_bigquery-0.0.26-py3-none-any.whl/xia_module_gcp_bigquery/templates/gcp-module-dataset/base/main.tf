provider "google" {
  alias = "google-dataset"
}

module "gcp_module_dataset" {
  providers = {
    google = google.google-dataset
  }

  source = "../../modules/gcp-module-dataset"

  config_dir = "../../../config/gcp/datasets"
  config_file = "../../../config/platform/gcp-project.yaml"
  landscape = local.landscape
  environment_dict = local.environment_dict
  current_env = local.current_env
}
