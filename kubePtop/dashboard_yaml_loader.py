import os
import yaml

class dashboardYamlLoader:
    def __init__(self) -> None:
        pass

    def dashboard_yaml_schema_validation(self, yaml):
        pass



    def load_dashboard_data(self, dashboard_name):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }

        # Check if the yaml file exists in the dashboards directory
        ## If so, return the file path
        ### The dashboard dir is taken as ENV
        yaml_file = dashboard_name
        # Check if the file does NOT exist
        if not os.path.isfile(yaml_file):
            out['fail_reason'] = f"Dashboard File '{yaml_file}' does NOT exist"
            return out

        # Read the file
        try:
            with open(yaml_file, 'r') as file:
                content = file.read()
                out['data'] = yaml.safe_load(content)
        except Exception as e:
            out['fail_reason'] = f"Failed to open the dashboard file '{yaml_file}' > {e}"
            return out

        # Yaml Schema validation


        # Loading variables args


        out['success'] = True
        return out
