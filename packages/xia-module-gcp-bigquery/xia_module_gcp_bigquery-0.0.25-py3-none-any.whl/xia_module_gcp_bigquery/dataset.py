from xia_module import Module


class Dataset(Module):
    activate_depends = ["gcp-module-project", "module-application-state-gcs"]
    module_name = "gcp-module-dataset"