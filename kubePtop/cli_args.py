import argparse
from sys import getallocatedblocks
import yaml
import rich
import os
import logging
from datetime import datetime
from pathlib import Path
from tabulate import tabulate
from kubePtop.global_attrs import GlobalAttrs
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
                "name": "list-dashboards",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-ld",
                    "required": False,
                    "description": "List dasboards names"
                }
            },
            {
                "name": "list-commands",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-lc",
                    "required": False,
                    "description": "List commands names"
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
            {
                "name": "debug",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-d",
                    "required": False,
                    "description": "Debug mode"
                }
            },
            {
                "name": "print-layout",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-pl",
                    "required": False,
                    "description": "Print empty layout structure"
                }
            },
            {
                "name": "version",
                "default": ".*",
                "cliArgument": {
                    "enable": True,
                    "short": "-V",
                    "required": False,
                    "description": "Print kptop version"
                }
            },
        ]
        self.variables = {}

    def build_parser(self, variables):
        parser = argparse.ArgumentParser(description='Process some CLI arguments.')
        for var in variables:
            if var['cliArgument']['enable']:
                if var['name'] in ['vhelp', 'list-dashboards', 'list-commands', 'debug', 'print-layout', 'version']:
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


    def _list_files_in_directory(self, directory_path):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }
        try:
            p = Path(directory_path)
            files_info = [
                {
                    "name": file.stem,
                    "creation_date": datetime.fromtimestamp(file.stat().st_ctime).strftime('%d-%m-%Y %H:%M:%S'),
                    "modification_date": datetime.fromtimestamp(file.stat().st_mtime).strftime('%d-%m-%Y %H:%M:%S')
                }
                for file in p.iterdir() if file.is_file() and file.suffix in ['.yaml', '.yml']
            ]
            if len(files_info) < 1:
                out['fail_reason'] = f"No files found in '{directory_path}'"
                return out

            out['data'] = files_info
            out["success"] = True
            return out
        except FileNotFoundError as e:
            out["fail_reason"] = f"Directory {directory_path} not found > {e}"
            return out

    def _load_file_content(self, directory_path, file_name):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }
        yaml_extensions = ['.yaml', '.yml']

        file_path = None
        for ext in yaml_extensions:
            try:
                potential_path = Path(directory_path) / (file_name + ext)
                if potential_path.exists():
                    file_path = potential_path
                    break
            except Exception as e:
                out["fail_reason"] = e
                return out

        if not file_path:
            out["fail_reason"] = f"File '{file_name}'.yml||yaml is NOT Found in {directory_path}"
            return out

        try:
            with open(file_path, 'r') as file:
                out["data"] = file.read()
                out["success"] = True
        except Exception as e:
            out["fail_reason"] = f"File is NOT Found"
        return out


    def run(self):
        initial_parser = self.build_parser(self.default_cli_args)
        # rich.print(initial_parser)
        initial_args, unknown_args = initial_parser.parse_known_args()

        if initial_args.command and initial_args.dashboard:
            rich.print("\n[yellow bold]Can NOT specify '--dashboard' & '--command' together\n")
            initial_parser.print_help()
            exit(1)

        if initial_args.list_dashboards and initial_args.list_commands:
                    rich.print("\n[yellow bold]Can NOT specify '--list-dashboards' & '--list-commands' together\n")
                    initial_parser.print_help()
                    exit(1)



        ################
        # Show Version #
        ################
        if initial_args.version:
            rich.print(GlobalAttrs.version)
            exit(1)

        ##############
        # Debug Mode #
        ##############
        if initial_args.debug:
            GlobalAttrs.debug = True

        ###################
        # List Dashboards #
        ###################
        if initial_args.list_dashboards:
            check = self._list_files_in_directory(GlobalAttrs.default_dashboards_dir)
            if not check['success']:
                rich.print(f"Could NOT list dashboards.\n[yellow]{check['fail_reason']}\n")
                exit(1)

            table = [['DASHBOARD', 'CREATION TIME', 'UPDATE TIME']]

            for file in check['data']:
                row = [file['name'], file['creation_date'], file['modification_date']]
                table.append(row)
            out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
            print(out)
            print()
            exit(0)

        #################
        # List Commands #
        #################
        if initial_args.list_commands:
            check = self._list_files_in_directory(GlobalAttrs.default_commands_dir)
            if not check['success']:
                rich.print(f"Could NOT list commands.\n[yellow]{check['fail_reason']}\n")
                exit(1)

            table = [['COMMAND', 'CREATION TIME', 'UPDATE TIME']]

            for file in check['data']:
                row = [file['name'], file['creation_date'], file['modification_date']]
                table.append(row)
            out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
            print(out)
            print()
            exit(0)

        ##################
        # Load Dashboard #
        ##################
        elif initial_args.dashboard:

            # Load dashboard yaml file
            check = self._load_file_content(GlobalAttrs.default_dashboards_dir, initial_args.dashboard)
            if not check['success']:
                rich.print(f"Dashboard is NOT found\n[yellow]{check['fail_reason']}\n")
                exit(1)

            # Parse and validate the dashboard yaml file
            parsed_dashboard = dashboard_yaml_loader.load_dashboard_data(command_content_content=check['data'])

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

            custom_dashboard_monitoring.build_custom_dashboard(dashboard_data=parsed_dashboard, dashboard_variables=self.variables, print_layout=initial_args.print_layout)

        ################
        # Load Command #
        ################
        elif initial_args.command:
            # Load command yaml file
            check = self._load_file_content(GlobalAttrs.default_commands_dir, initial_args.command)
            if not check['success']:
                rich.print(f"Command is NOT found\n[yellow]{check['fail_reason']}\n")
                exit(1)

            # Parse and validate the command yaml file
            parsed_command = command_yaml_loader.load_command_data(command_content_content=check['data'])
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
        elif unknown_args:
            rich.print(f"[yellow]ERROR -- Unknown args !!    {' '.join(unknown_args)}")
            initial_parser.print_usage()
