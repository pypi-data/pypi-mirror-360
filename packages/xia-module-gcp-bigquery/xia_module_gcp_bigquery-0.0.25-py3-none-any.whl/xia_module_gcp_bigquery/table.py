from xia_module import Module


class Table(Module):
    activate_depends = ["gcp-module-project", "module-application-state-gcs"]
    module_name = "gcp-module-table"
