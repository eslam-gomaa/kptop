import argparse
from kubePtop.read_env import ReadEnv
from kubePtop.session import PrometheusAPI
from kubePtop.node_monitor import Node_Monitoring
from kubePtop.pod_monitor import Pod_Monitoring
from kubePtop.pod_metrics import PrometheusPodsMetrics
import rich
from kubePtop.global_attrs import GlobalAttrs

# Read environment variables
read_environment_variables = ReadEnv()

node_monitor = Node_Monitoring()
pod_monitor = Pod_Monitoring()
prometheus_api = PrometheusAPI()
from kubePtop.logging import Logging


class Cli():
    def __init__(self):
        self.parser = None
        # CLI Input attributes
        # self.verify_prometheus = False
        self.list_nodes = False
        self.node = None
        self.list_pods = False
        self.pod = None
        self.container = None
        self.namespace = "default"
        self.all_namespaces = False
        self.debug = False
        self.dashboard = 'default'
        self.list_dashboards = False

        # Read CLI arguments
        self.argparse()
            
        # if self.verify_prometheus:
        #     prometheus_api.verify_exporters()
        #     exit(0)

        if self.debug:
            GlobalAttrs.debug = True
            Logging.log.setLevel(level="DEBUG")

        if self.node:
            if self.list_dashboards:
                node_monitor.list_dashboards()
                exit(0)
            # Check if the node found.
            node_monitor.display_dashboard(dashboard=self.dashboard, node_name=self.node)
            # node_monitor.node_monitor_dashboard_default(node_name=self.node)

        if self.pod and (self.container is None):
            # Check if the pod found.
            self.container = ".*"
            # rich.print(pod_monitor.podMetrics(pod=self.pod, container=self.container))
            
            # pod_metrics = PrometheusPodsMetrics()
            # print(pod_metrics.podPVC_table("strimzi-kafka-cluster-aws-prod-kafka-1"))
            # exit(1)
            pod_monitor.pod_monitor(pod=self.pod)

        if (self.pod) and (self.container):
            pod_monitor.pod_monitor(pod=self.pod, container=self.container)


        # Print help if no args are provided.
        self.parser.print_help()
        exit(0)


    def argparse(self):
        parser = argparse.ArgumentParser(description='A Python tool for Kubernetes Nodes/Pods terminal monitoring through Prometheus metrics.')
        parser.add_argument('top', type=str, nargs='*', metavar='{pods, pod, po}  |  {nodes, node}', help='top pods/nodes')
        parser.add_argument('-n', '--namespace', type=str, required=False, metavar='', help='Specify a Kubernetes namespace')
        parser.add_argument('-A', '--all-namespaces', required=False, action='store_true', help='All Kubernetes namespaces')
        parser.add_argument('-c', '--container', type=str, required=False, metavar='', help='Monitor a specific Pod\'s container')
        parser.add_argument('-i', '--interval', type=int, required=False, metavar='', help='Live monitoring update interval')
        parser.add_argument('-V', '--verify-prometheus', required=False, action='store_true', help='Verify Prometheus connection & exporters')
        parser.add_argument('-d', '--debug', required=False, action='store_true', help='Print debug output')

        parser.add_argument('-D', '--dashboard', type=str, required=False, metavar='', help='Specify a dashboard')
        parser.add_argument('-L', '--list-dashboards', required=False, action='store_true', help='List available dashboards')

        pod_aliases = ['pod', 'pods', 'po']
        node_aliases = ['node', 'nodes']

        results = parser.parse_args()
        self.parser = parser

        if results.debug:
            self.debug = True
            # GlobalAttrs.debug = True
            # print(GlobalAttrs.debug)
            # exit(1)

        if results.verify_prometheus:
            # self.verify_prometheus = True
            prometheus_api.verify_exporters()
            exit(0)

        if len(results.top) == 0:
            self.parser.print_help()
            exit(1)
        if len(results.top) == 1:
            if results.top[0] in pod_aliases:
                self.list_pods = True
            elif results.top[0] in node_aliases:
                self.list_nodes = True
            else:
                rich.print(f"[bold]ERROR -- unkown argument '{results.top[0]}'\n")
                self.parser.print_help()
        if len(results.top) == 2:
            if results.top[0] in pod_aliases:
                self.pod = results.top[1]
            elif results.top[0] in node_aliases:
                self.node = results.top[1]
            else:
                rich.print(f"[bold]ERROR -- unkown argument '{results.top[0]}'\n")
        if len(results.top) > 2:
            rich.print(f"[bold]ERROR -- unkown argument '{results.top[2]}' - only 2 arguments are expected\n")
            self.parser.print_help()
            exit(1)


        if results.namespace and results.all_namespaces:
            rich.print("[bold]ERROR -- You can only use '--all-namespaces' or '--namespace' \n")
            self.parser.print_help()
            exit(1)

        if results.namespace:
            self.namespace = results.namespace

        if results.all_namespaces:
            self.all_namespaces = results.all_namespaces

        if results.container:
            self.container = results.container

        if results.interval:
            GlobalAttrs.live_update_interval = results.interval

        if results.list_dashboards:
            self.list_dashboards = True

        if results.dashboard:
            self.dashboard = results.dashboard



cli = Cli()

def run():
    cli = Cli()