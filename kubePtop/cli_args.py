import argparse
import yaml
import rich
import os
import logging
from kubePtop.dashboard_monitor import customDashboardMonitoring
from kubePtop.command_run import commandRun
from kubePtop.dashboard_yaml_loader import dashboardYamlLoader
from kubePtop.command_yaml_loader import commandYamlLoader
dashboard_yaml_loader = dashboardYamlLoader()
command_yaml_loader = commandYamlLoader()
custom_dashboard_monitoring = customDashboardMonitoring()
custom_command_run = commandRun()

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

        ##################
        # Load Dashboard #
        ##################
        elif initial_args.dashboard:
            # rich.print(dashboard_yaml_loader.validate_dashboard_schema('d'))
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

        ################
        # Load Command #
        ################
        elif initial_args.command:
            parsed_command = command_yaml_loader.load_command_data(command_name="./command.yaml")
            # rich.print(parsed_command)
            # exit(1)

            if not parsed_command['success']:
                logging.error(f"Failed to load command: '{initial_args.command}'")
                logging.error(parsed_command['fail_reason'])
                exit(1)

            variables = parsed_command['data'].get('command').get('variables', [])
            if variables:
                # Combine default CLI args and dashboard variables
                all_variables = self.default_cli_args + variables
            else:
                all_variables = self.default_cli_args

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

            custom_command_run.run_custom_command(command_data=parsed_command, command_variables=self.variables)
        else:
            pass
