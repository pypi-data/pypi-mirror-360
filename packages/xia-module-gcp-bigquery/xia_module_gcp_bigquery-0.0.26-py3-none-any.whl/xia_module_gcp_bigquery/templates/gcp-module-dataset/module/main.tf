terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

locals {
  module_name = coalesce(var.module_name, basename(path.module))
  project_cfg = yamldecode(file(var.config_file))
  dataset_cfgs = { for file in fileset(var.config_dir, "**/*.yaml") :
      trimsuffix(basename(file), ".yaml") => yamldecode(file("${var.config_dir}/${file}"))
  }
  current_project = "${local.project_cfg["project_prefix"]}${var.current_env}"
}

resource "google_bigquery_dataset" "app_datasets" {
  for_each = local.dataset_cfgs

  project             = local.current_project
  dataset_id          = each.value["dataset_id"]
  description         = each.value["description"]
  friendly_name       = each.value["friendly_name"]
  location            = each.value["location"]
  delete_contents_on_destroy = each.value["delete_contents_on_destroy"]
  default_table_expiration_ms = lookup(each.value, "default_table_expiration_ms", null)
  default_partition_expiration_ms = lookup(each.value, "default_partition_expiration_ms", null)
}
