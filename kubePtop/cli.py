from kubePtop.global_attrs import GlobalAttrs
from kubePtop.read_env import ReadEnv
# Read environment variables
read_environment_variables = ReadEnv()
read_environment_variables.read_env()
import argparse
from kubePtop.session import PrometheusAPI
from kubePtop.node_monitor import Node_Monitoring
from kubePtop.pod_monitor import Pod_Monitoring
from kubePtop.node_metrics import PrometheusNodeMetrics
from kubePtop.pod_metrics import PrometheusPodsMetrics
import rich

node_monitor = Node_Monitoring()
pod_monitor = Pod_Monitoring()
pod_metrics = PrometheusPodsMetrics()
node_metrics = PrometheusNodeMetrics()
prometheus_api = PrometheusAPI()
from kubePtop.logging import Logging


class Cli():
    def __init__(self):
        self.parser = None
        # CLI Input attributes
        # self.verify_prometheus = False
        self.list_pvcs = False
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
        self.sort_by_mem_usage = False

        # Read CLI arguments
        self.argparse()


        if self.debug:
            GlobalAttrs.debug = True
            Logging.log.setLevel(level="DEBUG")

        # kptop nodes <NODE-NAME>
        if self.node:
            if self.list_dashboards:
                node_monitor.list_dashboards()
                exit(0)
            # Check if the node found.
            node_monitor.display_dashboard(dashboard=self.dashboard, node_name=self.node)

        if self.list_nodes:
            node_metrics.topNodeTable()
            exit(0)

        # kptop pods <POD-NAME>
        if self.pod:
            if self.container is None:
                self.container = ".*"
            # Check if the pod found.
            check_pod = pod_metrics.podExists(pod=self.pod, namespace=self.namespace)
            if not check_pod.get('result'):
                print(f"pod/{self.pod} not found in the '{self.namespace}' namespace")
                rich.print(f"[yellow]{check_pod.get('fail_reason')}")
                exit(1)
            pod_monitor.pod_monitor(pod=self.pod, namespace=self.namespace, container=self.container)
        
        if self.list_pods:
            # kptop pods
            ns = self.namespace
            if self.all_namespaces:
                ns = ".*"
            pod_metrics.topPodTable(namespace=ns,sort_by_mem_usage=self.sort_by_mem_usage)
            exit(0)

        if self.list_pvcs:
            # kptop pods
            ns = self.namespace
            if self.all_namespaces:
                ns = ".*"
            pod_metrics.topPvcTable(namespace=ns)
            exit(0)

        # Print help if no args are provided.
        # self.parser.print_help()

    def argparse(self):
        parser = argparse.ArgumentParser(description='A Python tool for Kubernetes Nodes/Pods terminal monitoring through Prometheus metrics.')
        parser.add_argument('top', type=str, nargs='*', metavar='{pods, pod, po}  |  {nodes, node}  |  {pvcs, pvc}', help='top pods/nodes/pvcs')
        parser.add_argument('-n', '--namespace', type=str, required=False, metavar='', help='Specify a Kubernetes namespace')
        parser.add_argument('-A', '--all-namespaces', required=False, action='store_true', help='All Kubernetes namespaces')
        parser.add_argument('-c', '--container', type=str, required=False, metavar='', help='Monitor a specific Pod\'s container')
        parser.add_argument('-i', '--interval', type=int, required=False, metavar='', help='Live monitoring update interval')
        parser.add_argument('-V', '--verify-prometheus', required=False, action='store_true', help='Verify Prometheus connection & exporters')
        parser.add_argument('-C', '--check-metrics', required=False, action='store_true', help='Checks the availability of the needed metrics')
        parser.add_argument('-d', '--debug', required=False, action='store_true', help='Print debug output')
        parser.add_argument('-s', '--sort-by-mem-usage', required=False, action='store_true', help='Sort top result by memory usage')

        # parser.add_argument('-D', '--dashboard', type=str, required=False, metavar='', help='Specify a dashboard')
        # parser.add_argument('-L', '--list-dashboards', required=False, action='store_true', help='List available dashboards')

        pod_aliases = ['pod', 'pods', 'po']
        node_aliases = ['node', 'nodes']
        pvc_aliases = ['pvc', 'pvcs']

        results = parser.parse_args()
        self.parser = parser

        if results.debug:
            self.debug = True
        
        ### kptop --verify-prometheus
        if results.verify_prometheus:
            prometheus_api.verify_exporters()
            if results.check_metrics:
                prometheus_api.check_metrics()
            exit(0)


        if len(results.top) == 0:
            self.parser.print_help()
            exit(1)

        ### kptop pods | nodes | pvcs
        if len(results.top) == 1:
            if results.top[0] in pod_aliases:
                self.list_pods = True
            elif results.top[0] in node_aliases:
                self.list_nodes = True
            elif results.top[0] in pvc_aliases:
                self.list_pvcs = True
            else:
                rich.print(f"[bold]ERROR -- unkown argument '{results.top[0]}'\n")
                self.parser.print_help()
                exit(1)
        
        ### Example: kptop pods <POD-NAME>
        if len(results.top) == 2:
            if results.top[0] in pod_aliases:
                self.pod = results.top[1]
            elif results.top[0] in node_aliases:
                self.node = results.top[1]
            else:
                rich.print(f"[bold]ERROR -- unkown argument '{results.top[0]}'\n")
                self.parser.print_help()
                exit(1)
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

        # if results.list_dashboards:
        #     self.list_dashboards = True

        # if results.dashboard:
        #     self.dashboard = results.dashboard

        if results.sort_by_mem_usage:
            self.sort_by_mem_usage = True



cli = Cli()

# def run():
#     cli = Cli()
