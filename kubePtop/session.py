import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import rich
from tabulate import tabulate
from kubePtop.global_attrs import GlobalAttrs
from rich.progress import SpinnerColumn, Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.live import Live
from kubePtop.logging import Logging
logging = Logging()
# Ignore Warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
# https://stackoverflow.com/a/41041028
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

import socket
import six.moves.urllib.request as urllib_request
import urllib.parse
from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import portforward
import traceback

class KubernetesPodPortForward:
    def __init__(self, api_object, pod_name, pod_port, namespace) :
        self.k8s_port_forward_socket = None
        self.core_v1 = api_object

        self.prometheus_pod_k8s_internal_endpoint = None

        self.namespace = namespace
        self.pod_name = pod_name
        self.pod_port = pod_port

    def createConnection(self, address, *args, **kwargs):
        pf = portforward(self.core_v1.connect_get_namespaced_pod_portforward,
                        self.pod_name, self.namespace, ports=str(self.pod_port))
        return pf.socket(int(self.pod_port))

    def runSocket(self):
        self.k8s_port_forward_socket = socket.create_connection = self.createConnection
        return self.k8s_port_forward_socket

    def sendRequest(self, path='/-/healthy'):
        try:
            if self.k8s_port_forward_socket is None:
                socket_ = self.runSocket()
                self.k8s_port_forward_socket = socket_
                rich.print(f"[grey69]INFO [Beta-Feature] -- Port-forward socket created for pod: '{self.pod_name}' namespace: '{self.namespace}'")
                logging.log.info(f"INFO [Beta-Feature] -- Port-forward socket created for pod: '{self.pod_name}' namespace: '{self.namespace}'")
                # print(self.k8s_port_forward_socket)

            url = f'http://{self.pod_name}.pod.{self.namespace}.kubernetes:{self.pod_port}'

            request = urllib_request.urlopen(
            url + path)

            class Response:
                    exit_code = request.code
                    reason = request.reason
                    text = request.read().decode('utf-8')

            res = Response()
            return res
        except ApiException as e:
            print(f"Erorr -- can't port-forward pod connection")
            print(e)
            exit(1)
        except KeyboardInterrupt as e:
            print(f"\nOk.")
            exit(1)
        except Exception as e:
            print(f"Error -- {e}")
            traceback.print_exc()
            # print(e)
            exit(1)
        # request.close()
        # print('Status Code: %s' % request.code)
        # print('Reason: %s' % request.reason)
        # print(text)

    def runQuery(self, query, path='/api/v1/query?'):
        try:
            if self.k8s_port_forward_socket is None:
                socket_ = self.runSocket()
                self.k8s_port_forward_socket = socket_
                # print(self.k8s_port_forward_socket)
                rich.print(f"[grey69]INFO [Beta-Feature] -- Port-forward socket created for pod: '{self.pod_name}' namespace: '{self.namespace}'")
                logging.log.info(f"INFO [Beta-Feature] -- Port-forward socket created for pod: '{self.pod_name}' namespace: '{self.namespace}'")

                # print(self.k8s_port_forward_socket)

            url = f'http://{self.pod_name}.pod.{self.namespace}.kubernetes:{self.pod_port}'
            params = urllib.parse.urlencode({'query': f'{query}'})

            # print(url + path + "%s" % params)
            # http://prometheus-server-0.pod.monitoring.kubernetes:9090/api/v1/query?query=node_cpu_seconds_total

            request = urllib_request.urlopen(
            url + path + "%s" % params)
            text = request.read().decode('utf-8')

            if request.code == 200:
                return json.loads(text)
            else:
                return {}
        except ApiException as e:
            print(f"Erorr -- can't port-forward pod connection")
            print(e)
            exit(1)
        except KeyboardInterrupt as e:
            print(f"\nOk.")
            exit(1)
        except Exception as e:
            print(f"Error -- {e}")
            traceback.print_exc()
            # print(e)
            exit(1)
        # request.close()
        # print('Status Code: %s' % request.code)
        # print('Reason: %s' % request.reason)
        # print(text)


class PrometheusAPI:

    def __init__(self):
        self.verify = False
        self.session = None
        self.prometheus_url = GlobalAttrs.env_prometheus_server
        self.prometheus_url_query = self.prometheus_url + "/api/v1/query"

        self.core_v1 = None

        # Pod-PortForward object
        self.pf = None
        # if GlobalAttrs.env_connection_method == "pod_portForward":
        #     self.K8s_authenticate()


    def K8s_authenticate(self):
        pod_name = GlobalAttrs.env_prometheus_pod_name
        pod_port = GlobalAttrs.env_prometheus_pod_port
        pod_namespace = GlobalAttrs.env_prometheus_pod_namespace

        if GlobalAttrs.env_kube_config_file:
            config.load_kube_config(
                config_file=GlobalAttrs.env_kube_config_file
            )
        else:
            config.load_kube_config()
        # c = Configuration.get_default_copy()
        # c.assert_hostname = False
        # Configuration.set_default(c)
        self.core_v1 = core_v1_api.CoreV1Api()

        self.pf = KubernetesPodPortForward(
                    api_object=self.core_v1,
                    pod_name=pod_name,
                    pod_port=pod_port,
                    namespace=pod_namespace)

        rich.print("[grey69]INFO [Beta-Feature] -- Authenticating K8s KubeConfig")
        Logging.log.info(f"INFO [Beta-Feature] -- Authenticating K8s KubeConfig")
        # Checking if the Prometheus pod exists
        pod_check = self.K8s_APIs_podExists(pod_name, pod_namespace)
        if not pod_check.get('found'):
            print(f"ERROR -- Prometheus Pod '{pod_name}' does NOT exist in the '{pod_namespace}' namespace ")
            Logging.log.error(f"ERROR -- Prometheus Pod '{pod_name}' does NOT exist in the '{pod_namespace}' namespace \n{pod_check.get('fail_reason')}")
            rich.print(f"[light_yellow3]{pod_check.get('fail_reason')}")
            exit(1)

    def K8s_APIs_podExists(self, pod_name, namespace):
        """Checks if a pod exists
        returns: (bool)
        """
        output = {
            "found": False,
            "fail_reason": ""
        }
        try:
            self.core_v1.read_namespaced_pod(name=pod_name,
                                            namespace=namespace)
            output['found'] = True
        except Exception as e:
            output['fail_reason'] = e
            # traceback.print_exc()
        return output

    def get_session(self):
        try:
            session = requests.Session()
            Logging.log.info("Establishing a new connection with Prometheus")
            self.session = session
            session.verify = self.verify
            prometheus_url = self.prometheus_url + "/-/healthy"
            if GlobalAttrs.debug:
                print(f"DEBUG -- Connecting to Prometheus: {prometheus_url}")
            Logging.log.info(f"Connecting to Prometheus: {prometheus_url}")
            if GlobalAttrs.env_basic_auth_enabled:
                req = session.get(prometheus_url, auth=(GlobalAttrs.env_prometheus_username, GlobalAttrs.env_prometheus_password))
            else:
                req = session.get(prometheus_url)
            if req.status_code == 200:
                Logging.log.info(f"connected successfully, status_code: {req.status_code}")
                if GlobalAttrs.debug:
                    print(f"DEBUG -- connected successfully, status_code: {req.status_code}")
                    print(f"DEBUG -- Response: \n{req.text}")
            else:
                print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; status_code: {req.status_code}, reason: {req.reason}\n")
                Logging.log.error(f"Failed to connect to Prometheus, status_code: {req.status_code}")
                if GlobalAttrs.debug:
                    Logging.log.debug("Exiting.")
                exit(1)
        except requests.exceptions.Timeout as e:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Timeout\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Timeout\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")
        except requests.exceptions.TooManyRedirects:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Too Many Redirects\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Too Many Redirects\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")
        except Exception as e:
            print(f"ERROR -- Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Connection Failed\n")
            Logging.log.error(f"Failed to connect to Prometheus '{GlobalAttrs.env_prometheus_server}'; Connection Failed\n")
            Logging.log.error(e)
            raise SystemExit(f"> {e}")

    def verify_prometheus_connection(self):
        out = {
            "connected": False,
            "status_code": "?",
            "reason": "",
            "fail_reason": ""
        }

        if GlobalAttrs.env_connection_method == 'pod_portForward':
            try:
                if GlobalAttrs.debug:
                    print("DEBUG -- Checking Prometheus existing connection")
                Logging.log.info("Checking Prometheus existing connection")
                path = "/-/healthy"
                prometheus_url = self.prometheus_url + path
                if GlobalAttrs.debug:
                    print(f"DEBUG -- Connecting to Prometheus: {prometheus_url}")

                req = self.get_request_raw_portForward(path=path)
                if req.exit_code == 200:
                    Logging.log.info(f"connected successfully, status_code: {req.exit_code}")
                    if GlobalAttrs.debug:
                        print(f"DEBUG -- connected successfully, status_code: {req.exit_code}")
                    out["connected"] = True
                    out["status_code"] = req.exit_code
                    out["reason"] = req.reason
                else:
                    out["status_code"] = req.exit_code
                    out["reason"] = req.reason
                    out["fail_reason"] = f"Failed to connect to Prometheus. Reason: {req.reason}"
                    Logging.log.error(f"Failed to connect to Prometheus. Reason: {req.reason}")
            except Exception as e:
                out["fail_reason"] = f"Failed to connect to Prometheus; {e}"
                out["reason"] = "unable to connnect"
                Logging.log.info(f"Failed to connect to Prometheus; {e}")

            return out

        elif GlobalAttrs.env_connection_method == 'prometheus_endpoint':
            session = requests.Session()
            session.verify = self.verify
            try:
                if GlobalAttrs.debug:
                    print("DEBUG -- Checking Prometheus existing connection")
                Logging.log.info("Checking Prometheus existing connection")
                prometheus_url = self.prometheus_url + "/-/healthy"
                if GlobalAttrs.debug:
                    print(f"DEBUG -- Connecting to Prometheus: {prometheus_url}")
                if GlobalAttrs.env_basic_auth_enabled:
                    req = session.get(prometheus_url, auth=(GlobalAttrs.env_prometheus_username, GlobalAttrs.env_prometheus_password))
                else:
                    req = session.get(prometheus_url)
                if req.status_code == 200:
                    Logging.log.info(f"connected successfully, status_code: {req.status_code}")
                    if GlobalAttrs.debug:
                        print(f"DEBUG -- connected successfully, status_code: {req.status_code}")
                    out["connected"] = True
                    out["status_code"] = req.status_code
                    out["reason"] = req.reason
                else:
                    out["status_code"] = req.status_code
                    out["reason"] = req.reason
                    out["fail_reason"] = f"Failed to connect to Prometheus. Reason: {req.reason}"
                    Logging.log.error(f"Failed to connect to Prometheus. Reason: {req.reason}")
            except Exception as e:
                out["fail_reason"] = f"Failed to connect to Prometheus; {e}"
                out["reason"] = "unable to connnect"
                Logging.log.info(f"Failed to connect to Prometheus; {e}")

            return out

    def run_query_pod_portForward(self, query):
        if self.core_v1 is None:
            self.K8s_authenticate()
        # pf = KubernetesPodPortForward(
        #     api_object=self.core_v1,
        #     pod_name=GlobalAttrs.env_prometheus_pod_name,
        #     pod_port=GlobalAttrs.env_prometheus_pod_port,
        #     namespace=GlobalAttrs.env_prometheus_pod_namespace)
        result = self.pf.runQuery(query)
        return result

    def get_request_raw_portForward(self, path='/api/v1/query?'):
        if self.core_v1 is None:
            self.K8s_authenticate()
        # pf = KubernetesPodPortForward(
        #     api_object=self.core_v1,
        #     pod_name=GlobalAttrs.env_prometheus_pod_name,
        #     pod_port=GlobalAttrs.env_prometheus_pod_port,
        #     namespace=GlobalAttrs.env_prometheus_pod_namespace)
        result = self.pf.sendRequest(path)
        return result

    def run_query_prometheus_endpoint(self, query):
        if self.session is None:
            if GlobalAttrs.debug:
                Logging.log.debug(f"While running a query .. establishing a new connection with Prometheus.")
                print(f"DEBUG -- While running a query .. establishing a new connection with Prometheus.")
            self.get_session()
        try:
            Logging.log.info(f"Running Query:\n\t\t  => {query}")
            if GlobalAttrs.env_basic_auth_enabled:
                req = self.session.get(self.prometheus_url_query, params={'query': f'{query}'}, auth=(GlobalAttrs.env_prometheus_username, GlobalAttrs.env_prometheus_password))
            else:
                req = self.session.get(self.prometheus_url_query, params={'query': f'{query}'})
            if req.status_code == 200:
                if GlobalAttrs.debug:
                    Logging.log.debug(f"Query run successfully, exit_code: {req.status_code}; Result:\n{json.loads(req.text)}")
                else:
                    Logging.log.info(f"Query run successfully, exit_code: {req.status_code}")
                return json.loads(req.text)
            else:
                Logging.log.error(f"Query did NOT run successfully, exit_code: {req.status_code}")
                return {}
        except requests.exceptions.Timeout as e:
            print(f"ERROR -- Failed to connect to Prometheus: Timeout\n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")
        except requests.exceptions.TooManyRedirects:
            print(f"ERROR -- Failed to connect to Prometheus: Too Many Redirects \n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")
        except (requests.exceptions.RequestException) as e:
            print(f"ERROR -- Failed to connect to Prometheus: Connection Failed\n")
            Logging.log.error(f"Query did NOT run successfully, {e}")
            raise SystemExit(f"> {e}")

    def run_query(self, query):
        if GlobalAttrs.env_connection_method == 'prometheus_endpoint':
            return self.run_query_prometheus_endpoint(query)
        elif GlobalAttrs.env_connection_method == 'pod_portForward':
            if self.core_v1 is None:
                self.K8s_authenticate()
            return self.run_query_pod_portForward(query)

    def verifyNodeExporter(self):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = 'sum(node_exporter_build_info) by (version)'

            if GlobalAttrs.env_connection_method == 'pod_portForward':
                result = self.run_query(query)
                if not result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric value:\n {query}"
                    return output

                if not result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data:\n {query}"
                    return output

                found_versions= {}
                for v in result.get('data').get('result'):
                    found_versions[v.get('metric').get('version')] = v.get('value')[1]
                output['result']['found_versions'] = found_versions
                output['success'] = True

            elif GlobalAttrs.env_connection_method == 'prometheus_endpoint':
                result = self.run_query(query)
                if not result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric value:\n {query}"
                    return output

                if not result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data:\n {query}"
                    return output

                found_versions= {}
                for v in result.get('data').get('result'):
                    found_versions[v.get('metric').get('version')] = v.get('value')[1]
                output['result']['found_versions'] = found_versions
                output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e

        return output

    def verifyKubernetesExporter(self):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = 'sum(kubernetes_build_info) by (git_version)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value:\n {query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data:\n {query}"
                return output

            found_versions= {}
            for v in result.get('data').get('result'):
                found_versions[v.get('metric').get('git_version')] = v.get('value')[1]
            output['result']['found_git_versions'] = found_versions
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e

        return output

    def verify_exporters(self):

        # Verify node_exporter
        # Check build info
        # Needed results
        # - avaialable not not
        # - version


        # if GlobalAttrs.env_connection_method == 'pod_portForward':
            # print(self.run_query_pod_portForward('machine_cpu_cores{instance="ip-10-129-184-213.eu-west-1.compute.internal"}'))

        print("")
        rich.print("[underline]Verifying Prometheus connection:[/underline] ...                    ", end="\r")
        prometheus_connection = self.verify_prometheus_connection()
        if prometheus_connection['connected']:
            rich.print("[underline]Verifying Prometheus connection:[/underline] [bold green]Connected                     ")
            rich.print_json(data=prometheus_connection)

            print("")
            rich.print("[underline]Verifying Prometheus Exporters:[/underline]")
            print("")
            rich.print("* Node Exporter:  ...               ", end="\r")
            verify_node_exporter = self.verifyNodeExporter()
            if verify_node_exporter.get('success'):
                rich.print("* Node Exporter:  [bold green]Found           ", end="\r")
            else:
                rich.print("* Node Exporter:  [bold red]Not Found           ", end="\r")
            print("")
            rich.print_json(data=verify_node_exporter)
            print("")
            rich.print("* Kubernetes Exporter: ...         ", end="\r")
            verify_kubernetes_exporter = self.verifyKubernetesExporter()
            if verify_kubernetes_exporter.get('success'):
                rich.print("* Kubernetes Exporter:  [bold green]Found           ", end="\r")
            else:
                rich.print("* Kubernetes Exporter:  [bold green]Not Found           ", end="\r")
            print("")
            rich.print_json(data=verify_kubernetes_exporter)
            print(" ")

        else:
            rich.print("[underline]Verifying Prometheus connection:[/underline] [bold red]Unable to connect                     ")
            rich.print_json(data=prometheus_connection)


    def check_metrics(self):
        """
        Checks the existence of the needed metrics
        -> Returns a structured table
        """

        # A List of the 'node_exporter' Prometheus metrics used by kptop
        node_exporter_metrics_lst =[
            'node_memory_MemFree_bytes',
            'node_memory_MemAvailable_bytes',
            'node_memory_MemTotal_bytes',
            'node_memory_Cached_bytes',
            'node_memory_Buffers_bytes',
            'node_memory_SwapTotal_bytes',
            'node_memory_SwapFree_bytes',
            'node_memory_SwapCached_bytes',
            'node_cpu_seconds_total',
            'node_load1',
            'node_load5',
            'node_load15',
            'machine_cpu_physical_cores',
            'machine_cpu_sockets',
            'up',
            'node_boot_time_seconds',
            'node_filesystem_size_bytes',
            'node_filesystem_avail_bytes',
            'node_filesystem_avail_bytes',
            'node_network_receive_bytes_total',
            'node_network_transmit_bytes_total',
            'node_disk_written_bytes_total',
            'node_disk_read_bytes_total',
            'machine_cpu_cores',
            'kubelet_running_pods',
        ]

        # A List of the 'Kubernetes exporter' Prometheus metrics used by kptop
        kubernetes_exporter_metrics_lst =[
            'container_last_seen',
            'container_memory_working_set_bytes',
            'container_memory_max_usage_bytes',
            'container_spec_memory_limit_bytes',
            'container_memory_cache',
            'container_spec_memory_swap_limit_bytes',
            'container_cpu_load_average_10s',
            'container_cpu_usage_seconds_total',
            'container_cpu_system_seconds_total',
            'container_cpu_user_seconds_total',
            'container_spec_cpu_quota',
            'kube_pod_spec_volumes_persistentvolumeclaims_info',
            'kubelet_volume_stats_capacity_bytes',
            'kubelet_volume_stats_used_bytes',
            'kubelet_volume_stats_available_bytes',
            'container_network_receive_bytes_total',
            'container_network_transmit_bytes_total',
            'container_start_time_seconds',
            'container_file_descriptors',
            'container_threads',
            'container_processes',
            'container_fs_reads_bytes_total',
            'container_fs_writes_bytes_total',
            'container_fs_writes_bytes_total',
        ]

        table = [['METRIC', 'EXPORTER', "STATE", 'COMMENT']]

        self.progress_metrics_check = Progress(
                SpinnerColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=30),
                TaskProgressColumn(),
                TextColumn("{task.fields[status]}"),
            )

        self.task_metrics_check_percentage  = self.progress_metrics_check.add_task(
                    description=f"[b]Checking Metrics ",
                    status="...",
                    total=len(node_exporter_metrics_lst) + len(kubernetes_exporter_metrics_lst),
                    )
        with Live(self.progress_metrics_check, auto_refresh=True, screen=False):
            try:
                cnt = 1
                # Check 'node_exporter' metrics
                for m in node_exporter_metrics_lst:
                    exporter = "node_exporter"
                    result = self.run_query(f"topk(1, {m})")
                    self.progress_metrics_check.update(task_id=self.task_metrics_check_percentage, status=f" [ [yellow]{m}[/yellow] ]", completed=cnt)

                    row = [m, exporter]
                    if result.get('status') != 'success':
                        row.append('not_available')
                        row.append('could not get metric value')

                    elif len(result.get('data').get('result')) < 1:
                        row.append('not_available')
                        row.append('did NOT return any data')
                    else:
                        row.append('available')
                        row.append('')

                    table.append(row)
                    cnt+=1

                # Check 'kubernetes_exporter' metrics
                for m in kubernetes_exporter_metrics_lst:
                    exporter = "kubernetes"
                    result = self.run_query(f"topk(1, {m})")
                    self.progress_metrics_check.update(task_id=self.task_metrics_check_percentage, status=f" [ [yellow]{m}[/yellow] ]", completed=cnt)

                    row = [m, exporter]
                    if result.get('status') != 'success':
                        row.append('not_available')
                        row.append('could not get metric value')

                    elif len(result.get('data').get('result')) < 1:
                        row.append('not_available')
                        row.append('did NOT return any data')
                    else:
                        row.append('available')
                        row.append('')

                    table.append(row)
                    cnt+=1
            except Exception as e:
                print(f"Error while priting 'metrics_check' progress\n{e}")
        tabulate.WIDE_CHARS_MODE = False
        out = tabulate(table, headers='firstrow', tablefmt='grid', showindex=False)
        print(out)
        exit(1)
