provider "google" {
  alias = "activate-google-table"
}

module "activate_gcp_module_table" {
  providers = {
    google = google.activate-google-table
  }

  source = "../../modules/activate-gcp-module-table"

  landscape = local.landscape
  applications = local.applications
  modules = local.modules
  environment_dict = local.environment_dict
  app_env_config = local.app_env_config
  module_app_to_activate = local.module_app_to_activate

  gcp_projects = module.gcp_module_project.gcp_projects

  depends_on = [module.gcp_module_project]
}

