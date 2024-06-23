import argparse
from logging import Logger
import yaml
import rich
import os
import logging
from kubePtop.dashboard_monitor import customDashboardMonitoring
from kubePtop.dashboard_yaml_loader import dashboardYamlLoader
dashboard_yaml_loader = dashboardYamlLoader()
custom_dashboard_monitoring = customDashboardMonitoring()
class Cli():
    def __init__(self):
        self.default_cli_args = [
            {
                "name": "dashboard",
                "default": "",
                "cliArgument": {
                    "enable": True,
                    "short": "-D",
                    "required": False,
                    "description": "dashboard name to display"
                }
            },
            {
                "name": "command",
                "default": "",
                "cliArgument": {
                    "enable": True,
                    "short": "-C",
                    "required": False,
                    "description": "command name to display"
                }
            },
            {
                "name": "vhelp",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-vh",
                    "required": False,
                    "description": "List the variables cli arguments of the dashboard/command manifests"
                }
            },
        ]
        self.variables = {}
        self.build_variables()

    # def parsed_dashboard_yaml_file(self, yaml_file):
    #     out = {
    #         "success": False,
    #         "data": None,
    #         "fail_reason": ""
    #     }

    #     # Check if the file does NOT exist
    #     if not os.path.isfile(yaml_file):
    #         out['fail_reason'] = f"Dashboard File '{yaml_file}' does NOT exist"
    #         return out

    #     # Read the file
    #     try:
    #         with open(yaml_file, 'r') as file:
    #             content = file.read()
    #             out['data'] = yaml.safe_load(content)
    #     except Exception as e:
    #         out['fail_reason'] = f"Failed to open the dashboard file '{yaml_file}' > {e}"
    #         return out

    #     out['success'] = True
    #     return out

    def build_parser(self, variables):
        parser = argparse.ArgumentParser(description='Process some CLI arguments.')
        for var in variables:
            if var['cliArgument']['enable']:
                if var['name'] == 'vhelp':
                    parser.add_argument(
                        f"--{var['name']}",
                        var['cliArgument']['short'],
                        required=var['cliArgument']['required'],
                        action='store_true',
                        help=var['cliArgument'].get('description', f'Specify the {var["name"]} variable value - default: "{var["default"]}"')
                    )
                else:
                    parser.add_argument(
                        f"--{var['name']}",
                        var['cliArgument']['short'],
                        required=var['cliArgument']['required'],
                        default=var['default'],
                        help=var['cliArgument'].get('description', f'Specify the {var["name"]} variable value - default: "{var["default"]}"')
                    )
        return parser



    def build_variables(self):
        initial_parser = self.build_parser(self.default_cli_args)
        # rich.print(initial_parser)
        initial_args, unknown_args = initial_parser.parse_known_args()

        if initial_args.command and initial_args.dashboard:
            rich.print("\n[yellow bold]Can NOT specify '--dashboard' & '--command' together\n")
            initial_parser.print_help()
            exit(1)

        elif initial_args.dashboard:
            parsed_dashboard = dashboard_yaml_loader.load_dashboard_data(dashboard_name="./dashboard.yaml")
            if not parsed_dashboard['success']:
                logging.error(f"Failed to load dashboard: '{initial_args.dashboard}'")
                logging.error(parsed_dashboard['fail_reason'])
                exit(1)

            variables = parsed_dashboard['data'].get('dashboard').get('variables', {})
            # Combine default CLI args and dashboard variables
            all_variables = self.default_cli_args + variables
            # Rebuild the parser with all variables
            final_parser = self.build_parser(all_variables)
            # Parse all arguments with the final parser
            final_args, unknown_args = initial_parser.parse_known_args()
            # Store the arguments in the variables dictionary
            args_dict = vars(final_args)

            if args_dict['vhelp']:
                final_parser.print_help()
                exit(0)

            for arg, value in args_dict.items():
                self.variables[arg] = value

            args = final_parser.parse_args()
            args_dict = vars(args)
            for arg, value in args_dict.items():
                if value == 'ALL':
                    value = ".*"
                self.variables[arg] = value

            custom_dashboard_monitoring.build_custom_dashboard(dashboard_data=parsed_dashboard, dashboard_variables=self.variables)

        elif initial_args.command:
            print('command')
        else:
            pass

        # # Step 3: Combine default CLI args and dashboard variables
        # all_variables = self.default_cli_args + variables

        # # Step 4: Rebuild the parser with all variables
        # final_parser = self.build_parser(all_variables)

        # # Step 5: Parse all arguments with the final parser
        # final_args = final_parser.parse_args()

        # # Step 6: Store the arguments in the variables dictionary
        # args_dict = vars(final_args)

        # if args_dict['vhelp']:
        #     final_parser.print_help()
        #     exit(0)

        # for arg, value in args_dict.items():
        #     self.variables[arg] = value

        # args = final_parser.parse_args()
        # args_dict = vars(args)
        # for arg, value in args_dict.items():
        #     if value == 'ALL':
        #         value = ".*"
        #     self.variables[arg] = value

        # return args


    def argparse(self):
        pass

# cli = Cli()
# cli.build_variables([])
# cli.build_variables()
# def run():
#     cli = Cli()
