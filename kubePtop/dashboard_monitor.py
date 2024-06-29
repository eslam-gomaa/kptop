import argparse
import re
from math import floor
import time
import threading
import rich
from rich.live import Live
# from rich.table import Table
from rich.panel import Panel
from rich.progress import SpinnerColumn, Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.layout import Layout
import os
from tabulate import tabulate
import yaml, json
import logging
import ast
from itertools import islice
from rich.console import Console, Group
from rich.rule import Rule
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
import traceback

from kubePtop.global_attrs import GlobalAttrs
from kubePtop.session import PrometheusAPI
from kubePtop.ascii_graph import AsciiGraph
from kubePtop.helper import Helper
helper_ = Helper()

from kubePtop.logging import Logging

class customDashboardMonitoring(PrometheusAPI):
    def __init__(self):
        super().__init__()
        self.layout_list = []
        self.data = {
            "graphs": {}
        }
        self.layout = None
        self.variables = {}
        self.threads = {}

    def run_query(self, query):
        if GlobalAttrs.env_connection_method == 'prometheus_endpoint':
            return self.run_query_prometheus_endpoint(query)
        elif GlobalAttrs.env_connection_method == 'pod_portForward':
            if self.core_v1 is None:
                self.K8s_authenticate()
            return self.run_query_pod_portForward(query)

        return query

    # def build_parser(self, variables):
    #     parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    #     for var in variables:
    #         if var['cliArgument']['enable']:
    #             if var['name'] == 'vhelp':
    #                 parser.add_argument(
    #                     f"--{var['name']}",
    #                     var['cliArgument']['short'],
    #                     required=var['cliArgument']['required'],
    #                     action='store_true',
    #                     help=var['cliArgument'].get('description', f'Specify the {var["name"]} variable value - default: "{var["default"]}"')
    #                 )
    #             else:
    #                 parser.add_argument(
    #                     f"--{var['name']}",
    #                     var['cliArgument']['short'],
    #                     required=var['cliArgument']['required'],
    #                     default=var['default'],
    #                     help=var['cliArgument'].get('description', f'Specify the {var["name"]} variable value - default: "{var["default"]}"')
    #                 )
    #     return parser

    # def build_variables(self, inital_args, variables):
    #     # Combine default CLI args and dashboard variables
    #     all_variables = inital_args + variables

    #     # Rebuild the parser with all variables
    #     final_parser = self.build_parser(all_variables)

    #     # Parse all arguments with the final parser, ignoring unknown args
    #     final_args, unknown_args = final_parser.parse_known_args()
    #     rich.print("Parsed arguments:", final_args)
    #     rich.print("Unknown arguments:", unknown_args)

    #     # Store the arguments in the variables dictionary
    #     args_dict = vars(final_args)
    #     if args_dict.get('vhelp'):
    #         final_parser.print_help()
    #         return

    #     for arg, value in args_dict.items():
    #         self.variables[arg] = value

    #     for arg, value in args_dict.items():
    #         if value == 'ALL':
    #             value = ".*"
    #         self.variables[arg] = value

    #     return final_args

    def build_custom_dashboard(self, dashboard_data, dashboard_variables, print_layout=False):

        # Build the Layout structure
        self.make_layout(layout_structure_dct=dashboard_data['data'], print_layout=print_layout)

        # vistualize the metrics on the layout
        self.variables = dashboard_variables
        self.update_layout_visualization(layout_structure_dct=dashboard_data['data'])


    def update_layout_visualization(self, layout_structure_dct):
        visualization_dct = layout_structure_dct['dashboard']['visualization']

        for visualization in visualization_dct:
            if visualization.get('enable', True):
                if visualization['type'] == 'asciiGraph':
                    if 'custom_key' in visualization:
                        self.build_ascii_graph_handler(name=visualization['name'], layout_box_name=visualization['box'], graph_options=visualization.get('asciiGraphOptions', {}), metric_unit=visualization['metricUnit'], metric=visualization['metric'], custom_key=visualization.get('custom_key', ''))
                    else:
                        self.build_ascii_graph_handler(name=visualization['name'], layout_box_name=visualization['box'], graph_options=visualization.get('asciiGraphOptions', {}), metric_unit=visualization['metricUnit'], metric=visualization['metric'])

                elif visualization['type'] == 'progressBarList':
                    if 'custom_key' in visualization:
                        self.build_progress_bar_list_handler(name=visualization['name'], layout_box_name=visualization['box'], progress_bar_list_options=visualization.get('progressBarListOptions', {}), metric_unit=visualization['metricUnit'], total_value_metric=visualization['metrics']['total_value_metric'], usage_value_metric=visualization['metrics']['usage_value_metric'], custom_key=visualization['custom_key'])
                    else:
                        self.build_progress_bar_list_handler(name=visualization['name'], layout_box_name=visualization['box'], progress_bar_list_options=visualization.get('progressBarListOptions', {}), metric_unit=visualization['metricUnit'], total_value_metric=visualization['metrics']['total_value_metric'], usage_value_metric=visualization['metrics']['usage_value_metric'])

                elif visualization['type'] == 'simpleTable':
                    self.build_simple_table_handler(name=visualization['name'], layout_box_name=visualization['box'], simple_table_options=visualization.get('simpleTableOptions', {}), metric_unit=visualization.get('metricUnit', 'None'), metric=visualization['metric'])

                elif visualization['type'] == 'advancedTable':
                    if 'custom_key' in visualization:
                        self.build_advanced_table_handler(name=visualization['name'], layout_box_name=visualization['box'], advanced_table_options=visualization.get('advancedTableOptions', {}), metric_unit=visualization.get('metricUnit', ''), columns=visualization['advancedTableColumns'], custom_key=visualization.get('custom_key', ''))
                    else:
                        self.build_advanced_table_handler(name=visualization['name'], layout_box_name=visualization['box'], advanced_table_options=visualization.get('advancedTableOptions', {}), metric_unit=visualization['metricUnit'], columns=visualization['columns'])

                else:
                    pass
        import time
        import traceback
        Logging.log.info("Starting the Layout.")
        try:
            with Live(self.layout, auto_refresh=True, screen=layout_structure_dct['dashboard']['layout'].get('fullScreen', True), refresh_per_second=GlobalAttrs.live_update_interval):
                while True:
                    Logging.log.info(f"waiting for the update interval '{GlobalAttrs.live_update_interval}' before updating the Layout ")
                    time.sleep(GlobalAttrs.live_update_interval)
                    Logging.log.info(f"Updating the layout")

        except Exception as e:
            rich.print("\n[yellow]ERROR -- " + str(e))
            rich.print("\n[underline bold]Exception:")
            traceback.print_exc()
            exit(1)
        except KeyboardInterrupt:
            print("                 ", end="\r")
            rich.print("Ok")
            exit(0)

    def parse_dashboard_yaml_file(self, yaml_file):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }

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

        out['success'] = True
        return out


    def validate_dashboard_yaml(self, yaml_file):
        pass

    def make_layout(self, layout_structure_dct, print_layout=False) -> Layout:
        """
        Build a custom layout structure
        """
        layout_dct = layout_structure_dct['dashboard']['layout']
        layout = Layout(name="root")

        if layout_dct['header']['enable']:
            layout.split(
                Layout(name="header", size=3, ratio=1),
                Layout(name="main", ratio=1),
            )
        else:
            layout.split(
                Layout(name="main", ratio=1),
            )

        layout["main"].split_row(
            Layout(name="body", ratio=3, minimum_size=100,),
        )

        left_enable = layout_dct['body']['boxes'].get('left', {}).get('enable', False)
        right_enable = layout_dct['body']['boxes'].get('right', {}).get('enable', False)
        middle_enable = layout_dct['body']['boxes'].get('middle', {}).get('enable', False)
        split_mode = layout_dct.get('split_mode', 'row')

        # If all are enabled
        if left_enable and right_enable and middle_enable:
            if split_mode == 'row':
                layout["body"].split_row(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
            elif split_mode == 'column':
                layout["body"].split_column(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
            self.layout_list = ['left', 'middle', 'right']

        # If two are enabled
        elif left_enable and right_enable:
            if split_mode == 'row':
                layout["body"].split_row(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
            elif split_mode == 'column':
                layout["body"].split_column(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
            self.layout_list = ['left', 'right']

        elif left_enable and middle_enable:
            if split_mode == 'row':
                layout["body"].split_row(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size'])
                )
            elif split_mode == 'column':
                layout["body"].split_column(
                    Layout(name="left", size=layout_dct['body']['boxes']['left']['size']),
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size'])
                )
            self.layout_list = ['left', 'middle']

        elif right_enable and middle_enable:
            if split_mode == 'row':
                layout["body"].split_row(
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
                self.layout_list = ['middle', 'right']
            elif split_mode == 'column':
                layout["body"].split_column(
                    Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size']),
                    Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
                )
                self.layout_list = ['middle', 'right']

        # If one is enabled
        elif left_enable:
            layout["body"].split_row(
                Layout(name="left", size=layout_dct['body']['boxes']['left']['size'])
            )
            self.layout_list = ['left']

        elif right_enable:
            layout["body"].split_row(
                Layout(name="right", size=layout_dct['body']['boxes']['right']['size'])
            )
            self.layout_list = ['right']

        elif middle_enable:
            layout["body"].split_row(
                Layout(name="middle", size=layout_dct['body']['boxes']['middle']['size'])
            )
            self.layout_list = ['middle']

        # If nothing is enabled
        else:
            self.layout_list = []

        if right_enable:
            if layout_dct['body']['boxes']['right'].get('split', {}):
                layout_objects =  []
                for box_name, box_info in layout_dct['body']['boxes']['right']['split'].items():
                    layout_objects.append(Layout(name=box_name, size=box_info['size'], ratio=box_info['ratio']))
                    self.layout_list.append(box_name)

                if layout_dct['body']['boxes']['right']['split_mode'] == "column":
                    layout['right'].split_column(*layout_objects)
                if layout_dct['body']['boxes']['right']['split_mode'] == "row":
                    layout['right'].split_row(*layout_objects)

        if left_enable:
            if layout_dct['body']['boxes']['left'].get('split', {}):
                layout_objects =  []
                for box_name, box_info in layout_dct['body']['boxes']['left']['split'].items():
                    layout_objects.append(Layout(name=box_name, size=box_info['size'], ratio=box_info['ratio']))
                    self.layout_list.append(box_name)

                if layout_dct['body']['boxes']['left']['split_mode'] == "column":
                    layout['left'].split_column(*layout_objects)
                if layout_dct['body']['boxes']['left']['split_mode'] == "row":
                    layout['left'].split_row(*layout_objects)

        if middle_enable:
            if layout_dct['body']['boxes']['middle'].get('split', {}):
                layout_objects =  []
                for box_name, box_info in layout_dct['body']['boxes']['middle']['split'].items():
                    layout_objects.append(Layout(name=box_name, size=box_info['size'], ratio=box_info['ratio']))
                    self.layout_list.append(box_name)

                if layout_dct['body']['boxes']['middle']['split_mode'] == "column":
                    layout['middle'].split_column(*layout_objects)
                if layout_dct['body']['boxes']['middle']['split_mode'] == "row":
                    layout['middle'].split_row(*layout_objects)

        if print_layout:
            # rich.print_json(json.dumps(layout_dct, indent=4))
            rich.print(layout)
            exit(0)

        self.layout = layout
        return layout

    # def convert_data_unit(self, value, metric_unit):
    #     if metric_unit == 'byte':
    #         value = helper_.bytes_to_kb_mb_gb(value)
    #     elif metric_unit == 'seconds':
    #         value =  helper_.seconds_to_human_readable(value)
    #     elif metric_unit == 'milliseconds':
    #         value =  helper_.milliseconds_to_human_readable(value)
    #     elif metric_unit == 'timestamp':
    #         value =  helper_.convert_epoch_timestamp(value)
    #     return value

    def safe_eval(self, custom_key, labels):
        for key, value in labels.items():
            custom_key = custom_key.replace(f"{{{{{key}}}}}", f"{value}")
        return custom_key

    def get_metric_data(self, metric, custom_key=None, evaluate_cli_argument_variables=False, value_from_label=""):
        out = {
            "success": False,
            "data": None,
            "fail_reason": "",
            "metric": ""
        }

        # Replace variables
        metric = self.replace_cli_argument_variable(metric)
        out['metric'] = metric
        # Run Metric
        metric_result = self.run_query(metric)

        if not metric_result.get('status') == 'success':
            out['fail_reason'] = "could not get metric value (Possible Syntax Error)"
            return out

        if not metric_result.get('data').get('result'):
            out['fail_reason'] = "metric did not return any data"
            return out

        dct = {}
        for i in metric_result['data']['result']:
            labels = i['metric']

            key = ""
            if custom_key:
                try:
                    # key = str(eval(custom_key))
                    key = helper_.safe_eval(custom_key, labels)
                except KeyError as e:
                    out['fail_reason'] = f"Label NOT found {e} --> Query: {metric}"
                    # key = f"Label NOT found: {e}"
                    # key = str(eval(custom_key.replace(e, 'not_found')))
                except SyntaxError as e:
                    out['fail_reason'] = f"Python Syntax Error: {e} --> {custom_key}"
                    key = "Python Syntax Error"

                except Exception as e:
                    out['fail_reason'] = f"failed to replace the key with custom_key: {e}"
                    key = str(e)

            else:
                key = str(i['metric'])

            if value_from_label:
                dct[key] = {
                    "timestamp":i['value'][0],
                    "value":i['metric'].get(value_from_label, 'label_not_found'),
                }
            else:
                dct[key] = {
                    "timestamp":i['value'][0],
                    "value":i['value'][1]
                }
        out['data'] = dct
        out['success'] = True
        return out

    def _find_variables_in_query(self, query):
        # Find all variables in the form $VARIABLE
        variables = re.findall(r'\$\w+', query)
        return variables

    def replace_cli_argument_variable(self, query):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }
        found_variables = self._find_variables_in_query(query)
        if found_variables:
            for variable in found_variables:
                if variable[1:] in self.variables:
                    # Replace the variable in the query string
                    query = query.replace(variable, self.variables[variable[1:]])
        return query

    def build_ascii_graph_handler(self, name, layout_box_name, graph_options, metric_unit, metric, custom_key=None):
        # Print loading message
        try:
            self.layout[layout_box_name].update(Panel(GlobalAttrs.initial_message, title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
        except KeyError as e:
            logging.error(e)
            print(f"ERROR -- while starting '{name}' box" + str(e))
            exit(1)
        # Start thread
        thread = threading.Thread(target=self.build_ascii_graph, args=(name, layout_box_name, graph_options, metric_unit, metric, custom_key))
        thread.name = name
        self.threads[name] = thread
        thread.daemon = True
        thread.start()

    def build_ascii_graph(self, name, layout_box_name, graph_options, metric_unit, metric, custom_key=None):
        graph = None
        while True:
            metric_data_dct = self.get_metric_data(metric=metric, custom_key=custom_key)

            if not metric_data_dct['success']:
                self.layout[layout_box_name].update(Panel(f"[red]Failed to get data from query 'total_value_metric': [bold]{metric_data_dct['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{metric_data_dct['metric']}", title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))

            data_graph = AsciiGraph()

            if graph_options:
                height_ = graph_options.get("height", 0)
                width_ = graph_options.get("width", 0)
                max_height_ = graph_options.get("maxHeight", 20)
                max_width_ = graph_options.get("maxWidth", 20)
                update_interval_ = graph_options.get("updateIntervalSeconds", 5)
            else:
                height_ = 17
                width_ = 45
                max_height_ = 20
                max_width_ = 50
                update_interval_ = 5

            # Save the graph object
            if not graph:
                data_graph.create_graph(names=list(metric_data_dct['data'].keys()), height=height_, width=width_, max_height=max_height_, max_width=max_width_, format=f'{{:8.0f}} {metric_unit}')
                graph = data_graph

            # Update the grap data
            for k, v in metric_data_dct['data'].items():
                graph.update_lst(k, float(v['value']), format=f'{{:8.0f}} {metric_unit}')

            # Organize the graph lines & items visualization
            data_group = Group(
                Text.from_ansi(graph.graph),
                Rule(style='#AAAAAA'),
                # Markdown("Bytes Written", justify='center'),
                Text.from_ansi(graph.colors_description_str)
            )

            self.layout[layout_box_name].update(Panel(data_group, title=f"[b]{name}", subtitle=f"Thread: {helper_.check_thread_status(self.threads[name])}", subtitle_align="left", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
            time.sleep(update_interval_)


    def build_progress_bar_list_handler(self, name, layout_box_name, progress_bar_list_options, metric_unit, total_value_metric, usage_value_metric, custom_key=None):
        # Print loading message
        self.layout[layout_box_name].update(Panel(GlobalAttrs.initial_message, title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
        # Start thread
        thread = threading.Thread(target=self.build_progress_bar_list, args=(name, layout_box_name, progress_bar_list_options, metric_unit, total_value_metric, usage_value_metric, custom_key))
        thread.name = name
        self.threads[name] = thread
        thread.daemon = True
        thread.start()

    def build_progress_bar_list(self, name, layout_box_name, progress_bar_list_options, metric_unit, total_value_metric, usage_value_metric, custom_key=None):

        while True:
            # Get usage data
            total_data = self.get_metric_data(total_value_metric, custom_key=custom_key)
            if not total_data['success']:
                self.layout[layout_box_name].update(Panel(f"[red]Failed to get data from query 'total_value_metric': [bold]{total_data['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{total_data['metric']}", title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))

            usage_data = self.get_metric_data(usage_value_metric, custom_key=custom_key)
            if not usage_data['success']:
                self.layout[layout_box_name].update(Panel(f"[red]Failed to get data from query 'total_value_metric': [bold]{total_data['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{total_data['metric']}", title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))

            data = {}
            for k, v in usage_data['data'].items():
                try:
                    data[k] = {
                        "value": v['value'],
                        "total": total_data['data'][k].get('value')
                    }
                except KeyError as e:
                    pass

            if progress_bar_list_options:
                max_items_list = progress_bar_list_options.get('maxItemsCount', 20)
                line_break = progress_bar_list_options.get('lineBreak', True)
                show_bar_percentage = progress_bar_list_options.get('showBarPercentage', True)
                bar_width = progress_bar_list_options.get('barWidth', 20)
                bar_width = progress_bar_list_options.get('barWidth', 20)
                update_interval_ = progress_bar_list_options.get("updateIntervalSeconds", 5)

            else:
                max_items_list = 20
                line_break = True
                show_bar_percentage = True
                bar_width = 20
                update_interval_ = 5

            progress_bars = []
            for progress_bar_name, progress_bar_data in islice(data.items(), max_items_list):
                if show_bar_percentage:
                    progress_bar = Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(bar_width=bar_width),
                        # TaskProgressColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TextColumn("{task.fields[status]}"),
                    )
                else:
                    progress_bar = Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(bar_width=bar_width),
                        TextColumn("{task.fields[status]}"),
                    )

                task_mem_total = progress_bar.add_task(description=f"[white]Mem Total  ", status="Loading", total=float(data[progress_bar_name]['total']))
                progress_bar.update(task_mem_total, completed=float(data[progress_bar_name]['value']), total=float(data[progress_bar_name]['total']), description=f"[white]{progress_bar_name}  ", status=f"  {helper_.bytes_to_kb_mb_gb(float(data[progress_bar_name]['value']))} / {helper_.bytes_to_kb_mb_gb(float(data[progress_bar_name]['total']))}")
                progress_bars.append(progress_bar)
                if line_break:
                    progress_bars.append(Rule(style='#AAAAAA'))


            data_group = Group(
                *progress_bars,
            )

            # return data_group
            self.layout[layout_box_name].update(Panel(data_group, title=f"[b]{name}", subtitle=f"Thread: {helper_.check_thread_status(self.threads[name])}", subtitle_align="left", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
            time.sleep(update_interval_)

    def build_simple_table_handler(self, name, layout_box_name, simple_table_options, metric_unit, metric, custom_key=None):
        # Print loading message
        self.layout[layout_box_name].update(Panel(GlobalAttrs.initial_message, title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
        # Start thread
        thread = threading.Thread(target=self.build_simple_table, args=(name, layout_box_name, simple_table_options, metric_unit, metric))
        thread.name = name
        self.threads[name] = thread
        thread.daemon = True
        thread.start()


    def build_simple_table(self, name, layout_box_name, simple_table_options, metric_unit, metric, custom_key=None):

        if simple_table_options:
            table_type_ = simple_table_options.get("tableType", 'plain')
            show_value_ = simple_table_options.get("showValue", True)
            header_upper_case_ = simple_table_options.get("headersUppercase", True)
            auto_convert_value_ = simple_table_options.get("autoConvertValue", True)
            show_table_index_ = simple_table_options.get("showTableIndex", True)
            update_interval_ = simple_table_options.get("updateIntervalSeconds", 5)
        else:
            table_type_ = 'plain'
            show_value_ = True
            header_upper_case_ = True
            auto_convert_value_ = True
            show_table_index_ = True
            update_interval_ = 5

        while True:
            # Get metric data
            metric_data_dct = self.get_metric_data(metric, custom_key=custom_key)
            if not metric_data_dct['success']:
                self.layout[layout_box_name].update(Panel(f"[red]Failed to get data from query 'total_value_metric': [bold]{metric_data_dct['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{metric_data_dct['metric']}", title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))

            first_dict_item = next(iter(metric_data_dct['data'].items()))[0]
            dict_keys = list(ast.literal_eval(first_dict_item).keys())

            if show_value_:
                dict_keys.append('values')

            if header_upper_case_:
                dict_keys = [key.upper() for key in dict_keys]


            table = [dict_keys]
            data = {}
            for labels, value in metric_data_dct['data'].items():
                labels_dct = ast.literal_eval(labels)
                row_list = list(labels_dct.values())
                if show_value_:
                    value_ = int(float(value['value']))
                    if auto_convert_value_:
                        if metric_unit == 'byte':
                            value_ = helper_.bytes_to_kb_mb_gb(value_)
                        elif metric_unit == 'cpu_seconds':
                            value_ = value_
                    row_list.append(value_)
                row = row_list
                table.append(row)


            out = tabulate(table, headers='firstrow', tablefmt=table_type_, showindex=show_table_index_)
            data_group = Group(
                out,
            )
            # return data_group
            self.layout[layout_box_name].update(Panel(data_group, title=f"[b]{name}", subtitle=f"Thread: {helper_.check_thread_status(self.threads[name])}", subtitle_align="left", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
            time.sleep(update_interval_)


    def build_advanced_table_handler(self, name, layout_box_name, advanced_table_options, metric_unit, columns, custom_key=None):
        # Print loading message
        self.layout[layout_box_name].update(Panel(GlobalAttrs.initial_message, title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
        # Start thread
        thread = threading.Thread(target=self.build_advanced_table, args=(name, layout_box_name, advanced_table_options, metric_unit, columns, custom_key))
        thread.name = name
        thread.daemon = True
        self.threads[name] = thread
        thread.start()

    def build_advanced_table(self, name, layout_box_name, advanced_table_options, metric_unit, columns, custom_key=None):

        if advanced_table_options:
            table_type_ = advanced_table_options.get("tableType", 'plain')
            # show_value_ = advanced_table_options.get("showValue", True)
            header_upper_case_ = advanced_table_options.get("headersUppercase", True)
            auto_convert_value_ = advanced_table_options.get("autoConvertValue", True)
            show_table_index_ = advanced_table_options.get("showTableIndex", True)
            update_interval_ = advanced_table_options.get("updateIntervalSeconds", 5)
        else:
            table_type_ = 'plain'
            # show_value_ = True
            header_upper_case_ = True
            auto_convert_value_ = True
            show_table_index_ = True
            update_interval_ = 5

        box_name = name
        data = {}

        columns_dct = {}
        for column in columns:
            key = next(iter(column))
            new_dct = {k: v for k, v in column.items() if k != key}
            columns_dct[key] = new_dct

        header = list(columns_dct.keys())
        header.insert(0, 'name')

        if header_upper_case_:
            header = [key.upper() for key in header]

        while True:
            table = [header]
            for column, column_info in columns_dct.items():

                metric_data = self.get_metric_data(column_info['metric'], custom_key=custom_key, value_from_label=column_info.get('valueFromLabel', ''))

                if not metric_data['success']:
                    self.layout[layout_box_name].update(Panel(f"[red]Failed to get data from query 'total_value_metric': [bold]{metric_data['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{metric_data['metric']}", title=f"[b]{name}", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))

                for name, value in metric_data['data'].items():
                    try:
                        value_ = float(value['value'])
                        if auto_convert_value_:
                            value_ = helper_.convert_data_unit(value=value_, metric_unit=column_info['metricUnit'])
                    except:
                        value_ = value['value']

                    try:
                        data[name][column] = value_
                    except KeyError:
                        data[name] = {
                            column: value_
                        }

            for name, value in data.items():
                row = [name] + [value.get(col, '?') for col in columns_dct.keys()]  # Ensure order matches headers
                table.append(row)

            out = tabulate(table, headers='firstrow', tablefmt=table_type_, showindex=show_table_index_)
            data_group = Group(
                out
            )
            self.layout[layout_box_name].update(Panel(data_group, title=f"[b]{box_name}", subtitle=f"Thread: {helper_.check_thread_status(self.threads[box_name])}", subtitle_align="left", padding=(1, 1), expand=True, safe_box=True, highlight=True, height=0))
            time.sleep(update_interval_)
