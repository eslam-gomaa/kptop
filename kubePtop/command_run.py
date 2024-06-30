import re
import rich
import os
from tabulate import tabulate
import logging
from kubePtop.global_attrs import GlobalAttrs
from kubePtop.session import PrometheusAPI
# from kubePtop.ascii_graph import AsciiGraph
from kubePtop.helper import Helper
helper_ = Helper()

from kubePtop.logging import Logging

class commandRun(PrometheusAPI):
    def __init__(self):
        super().__init__()
        self.layout_list = []
        self.data = {
            "graphs": {}
        }
        self.layout = None
        self.variables = {}

    def run_query(self, query):
        if GlobalAttrs.env_connection_method == 'prometheus_endpoint':
            return self.run_query_prometheus_endpoint(query)
        elif GlobalAttrs.env_connection_method == 'pod_portForward':
            if self.core_v1 is None:
                self.K8s_authenticate()
            return self.run_query_pod_portForward(query)

        return query

    def run_custom_command(self, command_data, command_variables):
        self.variables = command_variables
        command_dct = command_data['data']['command']
        if command_dct['execute']['type'] == 'advancedTable':
            self.build_advanced_table_command(name=command_dct['name'], layout_box_name=None, advanced_table_options=command_dct['execute'].get('advancedTableOptions', {}), metric_unit='kb', columns=command_dct['execute'].get('advancedTableColumns', {}), custom_key=command_dct['execute']['custom_key'])


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

    def build_advanced_table_command(self, name, layout_box_name, advanced_table_options, metric_unit, columns, custom_key=None):

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

        table = [header]
        for column, column_info in columns_dct.items():
            # metric_data = self.get_metric_data(column_info['metric'], custom_key=custom_key)
        #     metric_data = self.get_metric_data(column_info['metric'], custom_key=custom_key, value_from_label=column_info.get('valueFromLabel', ''))


            # if not metric_data['success']:
            #     rich.print(f"[red]Failed to get data from query 'total_value_metric': [bold]{metric_data['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{metric_data['metric']}")
            #     exit(1)

        #     for name, value in metric_data['data'].items():
        #         value_ = float(value['value'])
        #         if auto_convert_value_:
        #             value_ = helper_.convert_data_unit(value=value_, metric_unit=column_info['metricUnit'])
        #         try:
        #             data[name][column] = value_
        #         except KeyError:
        #             data[name] = {
        #                 column: value_
        #             }

        # for name, value in data.items():
        #     row = [name] + [value.get(col, '?') for col in columns_dct.keys()]  # Ensure order matches headers
        #     table.append(row)
            metric_data = self.get_metric_data(column_info['metric'], custom_key=custom_key, value_from_label=column_info.get('valueFromLabel', ''))

            if not metric_data['success']:
                rich.print(f"[red]Failed to get data from query 'total_value_metric': [bold]{metric_data['fail_reason']}[/bold][/red]\n\n[bold]METRIC:[/bold]\n[grey53]{metric_data['metric']}")
                exit(1)

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
        rich.print(out)
