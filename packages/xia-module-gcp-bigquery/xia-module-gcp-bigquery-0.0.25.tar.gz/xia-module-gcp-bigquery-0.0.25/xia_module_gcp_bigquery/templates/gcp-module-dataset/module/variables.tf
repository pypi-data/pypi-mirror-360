variable "module_name" {
  type = string
  description = "Module Name"
  default = ""
}

variable "config_file" {
  type = string
  description = "Module config file"
  default = ""
}

variable "config_dir" {
  type = string
  description = "Module config dictionary"
  default = ""
}

variable "landscape" {
  type = any
  description = "Landscape Configuration"
}

variable "environment_dict" {
  type = any
  description = "Environment Configuration"
}

variable "current_env" {
  type = string
  description = "Current Environment Name"
}