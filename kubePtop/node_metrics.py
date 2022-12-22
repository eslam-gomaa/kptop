from kubePtop.session import PrometheusAPI
from kubePtop.global_attrs import GlobalAttrs
from kubePtop.logging import Logging
from kubePtop.helper import Helper
from tabulate import tabulate
from kubePtop.colors import Bcolors
bcolors = Bcolors()
import traceback



helper_ = Helper()

class PrometheusNodeMetrics(PrometheusAPI):
    
    def __init__(self):
        super().__init__()


    def nodeMetrics(self, node):
        """
        Return Node metrics
        INPUT:
            - Node name (str)
        Return: Node metrics (dct)
        """
        output = {}

        output['cpu'] = {
            'cpuLoadAvg1m': self.cpuLoadAvg1m(node),
            'cpuLoadAvg5m': self.cpuLoadAvg5m(node),
            'cpuLoadAvg15m': self.cpuLoadAvg15m(node),
            'cpuUsageAVG': self.cpuUsageAVG(node)
        }
        
        output['memory'] = {
            'MemFreeBytes': self.MemFreeBytes(node),
            'MemAvailableBytes': self.MemAvailableBytes(node),
            'MemTotalBytes': self.MemTotalBytes(node),
            'MemCachedBytes': self.MemCachedBytes(node),
            'MemBuffersBytes': self.MemBuffersBytes(node),
            'MemSwapTotalBytes': self.MemSwapTotalBytes(node),
            'MemSwapFreeBytes': self.MemSwapFreeBytes(node),
            'MemSwapCachedBytes': self.MemSwapCachedBytes(node)
        }

        output['disk'] = {}

        output['fs'] = {
            'nodeFsSize': self.nodeFsSize(node),
            'nodeFsUsed': self.nodeFsUsed(node),
            'nodeFsAvailable': self.nodeFsAvailable(node),
        }
        

        return output

    ### TO BE CLEANED ###
    # def node_type(self, node="master"):
    #     """
    #     Detects node type ie. master/worker
    #     INPUT:
    #         - K8s node name (str)
    #     Return:
    #         - node type eg. "worker" (str)
    #     """
    #     all_nodes = self.list_nodes_names()
    #     if node not in all_nodes.get('result'):
    #         raise SystemExit(f"ERROR -- Node '{node}' is not found")

    #     role = "worker"
    #     worker_nodes = self.run_query(f'node_memory_MemTotal_bytes{{node="{node}"}}')
    #     if len(worker_nodes.get('data').get('result')) < 1:
    #         role = "master" 

    #     return role


    ### NOT USED ###
    def list_nodes_names(self, node, devices_filter="eth.*"):
        """
        Returns Nodes names:
        INPUT:
            - K8s node name (str)
        Return:
            - List of nodes names (lst)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": []
        }
        try:
            result = self.run_query('machine_memory_bytes')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output

            for node in result.get('data').get('result'):
                output['result'].append(node.get('metric').get('kubernetes_io_hostname'))
                output['success'] = True


        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output
    
    def MemFreeBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_MemFree_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemAvailableBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_MemAvailable_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemTotalBytes(self, node):
        """
        Returns node total memory (worker nodes only)
        INPUT:
            - K8s node name (str)
        Return:
            - metric (str)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_MemTotal_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemCachedBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_Cached_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemBuffersBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_Buffers_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemSwapTotalBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_SwapTotal_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemSwapFreeBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_SwapFree_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def MemSwapCachedBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_memory_SwapCached_bytes{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def cpuUsageAVG(self, node, avg_time="10m"):
        """
        Return cpu info
        INPUT:
            - k8s node name (str)
        Return:
            - dct of dcts (nested dct for each core) (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            # Returns cpu usage percentage.
            result = self.run_query(f'100 - (avg by (kubernetes_node) (irate(node_cpu_seconds_total{{mode="idle", {GlobalAttrs.node_exporter_node_label}="{node}"}}[{avg_time}])) * 100 )')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
            
            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def cpuLoadAvg1m(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_load1{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = result.get('data').get('result')[0].get('value')[1]
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def cpuLoadAvg5m(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_load5{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = result.get('data').get('result')[0].get('value')[1]
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def cpuLoadAvg15m(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_load15{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = result.get('data').get('result')[0].get('value')[1]
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    ### NOT Used
    # def cpuCores(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": ""
    #     }
    #     try:
    #         result = self.run_query(f'kube_node_status_capacity_cpu_cores{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = "could not get metric value"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = "metric did not return any data"
    #             return output
                
    #         output['result'] = int(result.get('data').get('result')[0].get('value')[1])
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())
    #     return output
    
    def cpu_physical_cores(self, node):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'machine_cpu_physical_cores{{kubernetes_io_hostname="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output
    
    def cpu_sockets(self, node):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'machine_cpu_sockets{{kubernetes_io_hostname="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    ### NOT USED ###
    # def nodeOSMetrics(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {}
    #     output['nodeUp'] = self.nodeUp(node)
    #     output['bootTimeSeconds'] = self.bootTimeSeconds(node)
    #     # output['osInfo'] = self.osInfo(node_label, node)
    #     # output['osVersion'] = self.osVersion(node_label, node)
    #     output['unameInfo'] = self.unameInfo(node)
    #     # output['kubeNodeInfo'] = self.kubeNodeInfo(node_label, node)
    #     output['nodeExporterBuildInfo'] = self.nodeExporterBuildInfo(node)

    #     return output

    def nodeUp(self, node):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'up{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            if int(result.get('data').get('result')[0].get('value')[1]) == 1:
                output['result'] = True
            else:
                output['result'] = False
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def bootTimeSeconds(self, node):
        """
        not in use at the moment
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": []
        }
        try:
            result = self.run_query(f'node_boot_time_seconds{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1])
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    ### NOT USED ###
    # def osInfo(self, node):
    #     """
    #     not in use at the moment
    #     may be skipped.
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": {}
    #     }
    #     try:
    #         result = self.run_query(f'node_os_info{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = "could not get metric value"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = "metric did not return any data"
    #             return output
                
    #         output['result'] = {
    #             "pretty_name": result.get('data').get('result')[0].get('metric').get('pretty_name'),
    #             "version": result.get('data').get('result')[0].get('metric').get('version'),
    #             "version_codename": result.get('data').get('result')[0].get('metric').get('version_codename'),
    #             "version_id": result.get('data').get('result')[0].get('metric').get('version_id'),
    #             }
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output

    # def osVersion(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": {}
    #     }
    #     try:
    #         result = self.run_query(f'node_os_version{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = "could not get metric value"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = "metric did not return any data"
    #             return output
                
    #         output['result'] = {
    #             "id": result.get('data').get('result')[0].get('metric').get('id'),
    #             "id_like": result.get('data').get('result')[0].get('metric').get('id_like'),
    #             }
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output

    # def unameInfo(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": {}
    #     }
    #     try:
    #         result = self.run_query(f'node_uname_info{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = "could not get metric value"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = "metric did not return any data"
    #             return output
                
    #         output['result'] = {
    #             "sysname": result.get('data').get('result')[0].get('metric').get('sysname'),
    #             "release": result.get('data').get('result')[0].get('metric').get('release'),
    #             "nodename": result.get('data').get('result')[0].get('metric').get('nodename'),
    #             "machine": result.get('data').get('result')[0].get('metric').get('machine'),
    #             "version": result.get('data').get('result')[0].get('metric').get('version'),
    #             }
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output

    # def kubeNodeInfo(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": {}
    #     }
    #     try:
    #         result = self.run_query(f'kube_node_info{{{GlobalAttrs.node_exporter_node_label}="{node}"}}')
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = "could not get metric value"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = "metric did not return any data"
    #             return output
                
    #         output['result'] = {
    #             "container_runtime_version": result.get('data').get('result')[0].get('metric').get('container_runtime_version'),
    #             "internal_ip": result.get('data').get('result')[0].get('metric').get('internal_ip'),
    #             "kernel_version": result.get('data').get('result')[0].get('metric').get('kernel_version'),
    #             "kubelet_version": result.get('data').get('result')[0].get('metric').get('kubelet_version'),
    #             "kubeproxy_version": result.get('data').get('result')[0].get('metric').get('kubeproxy_version'),
    #             "os_image": result.get('data').get('result')[0].get('metric').get('os_image'),
    #             }
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output

    # def nodeExporterBuildInfo(self, node):
    #     """
    #     not in use at the moment
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": {}
    #     }
    #     try:
    #         query = f'node_exporter_build_info{{{GlobalAttrs.node_exporter_node_label}="{node}"}}'
    #         result = self.run_query(query)
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] = f"could not get metric value:\n {query}"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data:\n {query}"
    #             return output
                
    #         output['result'] = {
    #             "version": result.get('data').get('result')[0].get('metric').get('version'),
    #             "revision": result.get('data').get('result')[0].get('metric').get('revision'),
    #             "goversion": result.get('data').get('result')[0].get('metric').get('goversion'),
    #             }
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output

    def nodeFsSize(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_filesystem_size_bytes{{mountpoint="/",fstype!="rootfs",{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def nodeFsAvailable(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_filesystem_avail_bytes{{mountpoint="/",fstype!="rootfs",{GlobalAttrs.node_exporter_node_label}="{node}"}}')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def nodeFsUsed(self, node):
        """
        Returns Node Used Filesystem in bytes
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            result = self.run_query(f'node_filesystem_size_bytes{{mountpoint="/",fstype!="rootfs",{GlobalAttrs.node_exporter_node_label}="{node}"}} - node_filesystem_avail_bytes')
            if not result.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output
                
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def PodMemUsage(self, node, sort_desc=False):
        """
        Return Pod memory usage in bytes (running on the node)
        INPUT:
            - K8s node name (str)
            - sort_desc: (bool) sort with Pods memory usage
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        
        try:
            query = f'sum(container_spec_memory_limit_bytes{{container!="", {GlobalAttrs.kubernetes_exporter_node_label}="{node}"}}) by (pod, instance, namespace)'
            memory_limit = self.run_query(query)
            # memory_max_usage = self.run_query('sum(container_memory_max_usage_bytes{container!="", instance="ip-192-168-104-139.me-south-1.compute.internal"}) by (pod, instance, namespace)')
            # memory_cache = self.run_query('sum(container_memory_cache{container!="", instance="ip-192-168-104-139.me-south-1.compute.internal"}) by (pod, instance, namespace)')
            
            if sort_desc:
                memory_usage = self.run_query(f'sort_desc(sum(container_memory_working_set_bytes{{container!="", {GlobalAttrs.kubernetes_exporter_node_label}="{node}"}}) by (pod, instance, namespace))')
            else:
                memory_usage = self.run_query(f'sum(container_memory_working_set_bytes{{container!="", {GlobalAttrs.kubernetes_exporter_node_label}="{node}"}}) by (pod, instance, namespace)')

            if not memory_usage.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{query}"
                return output

            if not memory_usage.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                return output

            dct = {}
            if len(memory_usage.get('data').get('result')) > 0 and (len(memory_limit.get('data').get('result'))) > 0:
                for pod_mem_usage in memory_usage.get('data').get('result'):
                    dct[pod_mem_usage.get('metric').get('pod')] = {
                        "namespace": pod_mem_usage.get('metric').get('namespace'),
                        "instance": pod_mem_usage.get('metric').get('instance'),
                        "memory_usage": int(pod_mem_usage.get('value')[1]),
                        "memory_limit": 0
                    }
                for pod_mem_limit in memory_limit.get('data').get('result'):
                    dct[pod_mem_limit.get('metric').get('pod')]["memory_limit"] = int(pod_mem_limit.get('value')[1])             
            
            output['result'] = dct
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def PodCpuUsageAvg(self, node, avg="10m"):
        """
        Returns Pod CPU usgae average
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            pods_cpu_avg = self.run_query(f'sum(irate(container_cpu_usage_seconds_total{{pod!="", {GlobalAttrs.kubernetes_exporter_node_label}="{node}"}}[{avg}])) by (pod, namespace, instance)')
            node_cores = self.run_query(f'sum (machine_cpu_cores{{instance="{GlobalAttrs.kubernetes_exporter_node_label}"}})')
            
            if not pods_cpu_avg.get('status') == 'success':
                output['fail_reason'] = "could not get metric value"
                return output

            if not pods_cpu_avg.get('data').get('result'):
                output['fail_reason'] = "metric did not return any data"
                return output

            dct = {}
            if len(pods_cpu_avg.get('data').get('result')) > 0:
                cpu_cores_n = node_cores.get('data').get('result')[0].get('value')[1]
                for pod in pods_cpu_avg.get('data').get('result'):
                    dct[pod.get('metric').get('pod')] = {
                        "node": pod.get('metric').get('instance'),
                        "namespace": pod.get('metric').get('namespace'),
                        "namespace": pod.get('metric').get('namespace'),
                        "cpu_usage_avg": (float(pod.get('value')[1])) // int(cpu_cores_n) * 100,
                    }

            output['success'] = True
            output['result'] = dct

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def PodMemTopUsage(self, node):
        """
        Print a table with Top Pods with memory usage (default: top 10 pods)
        INPUT:
            - K8s node name (str)
        OUTPUT: prints a text table.
        RETURN: No Return
        """
        table = [['POD', "NAMESPACE", 'MEMORY_USAGE', 'PERCENTAGE', 'MEMORY_LIMIT']]

        pods_metircs = self.PodMemUsage(node, sort_desc=True)

        if not pods_metircs.get('success'):
            return pods_metircs.get('fail_reason')

        for pod, metrics in pods_metircs.get('result').items():
            if metrics.get('memory_limit') == 0:
                memory_limit = "--"
            else:
                memory_limit = helper_.bytes_to_kb_mb_gb(metrics.get('memory_limit'))

            if metrics.get('memory_limit') != 0:
                memory_usage_percentage = str(int(100 * (metrics.get('memory_usage') / metrics.get('memory_limit')))) + "%"
            else:
                memory_usage_percentage = "--"

            row = [pod, metrics.get('namespace'), helper_.bytes_to_kb_mb_gb(metrics.get('memory_usage')), memory_usage_percentage, memory_limit]
            table.append(row)

        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=True)
        return out
            
    def nodeNetworkReceiveBytes(self, node, devices_to_ingore="tap.*|veth.*|br.*|docker.*|virbr*|lo*|eni.*"):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(node_network_receive_bytes_total{{{GlobalAttrs.node_exporter_node_label}=~"{node}",device!~"{devices_to_ingore}"}}[10m])) by ({GlobalAttrs.node_exporter_node_label}, device)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] =  f"could not get metric's value: \n{query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                return output
            
            devices = {}
            for device in result.get('data').get('result'):
                devices[device.get('metric').get('device')] = float(device.get('value')[1]) 

            output['result'] = devices
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    def nodeNetworkTransmitBytes(self, node, devices_to_ingore="tap.*|veth.*|br.*|docker.*|virbr*|lo*|eni.*"):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(node_network_transmit_bytes_total{{{GlobalAttrs.node_exporter_node_label}=~"{node}",device!~"{devices_to_ingore}"}}[10m])) by ({GlobalAttrs.node_exporter_node_label}, device)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] =  f"could not get metric's value: \n{query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                return output
            
            devices = {}
            for device in result.get('data').get('result'):
                devices[device.get('metric').get('device')] = float(device.get('value')[1]) 

            output['result'] = devices
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output


    def nodeDiskWrittenBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(node_disk_written_bytes_total{{{GlobalAttrs.node_exporter_node_label}=~"{node}"}}[10m])) by ({GlobalAttrs.node_exporter_node_label}, device)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] =  f"could not get metric's value: \n{query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                return output
            
            devices = {}
            for device in result.get('data').get('result'):
                devices[device.get('metric').get('device')] = float(device.get('value')[1]) 

            output['result'] = devices
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output


    def nodeDiskReadBytes(self, node):
        """
        INPUT:
            - K8s node name (str)
        Return:
            - metric (dct)
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(node_disk_read_bytes_total{{{GlobalAttrs.node_exporter_node_label}=~"{node}"}}[10m])) by ({GlobalAttrs.node_exporter_node_label}, device)'
            result = self.run_query(query)
            if not result.get('status') == 'success':
                output['fail_reason'] =  f"could not get metric's value: \n{query}"
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                return output
            
            devices = {}
            for device in result.get('data').get('result'):
                devices[device.get('metric').get('device')] = float(device.get('value')[1]) 

            output['result'] = devices
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output

    ### NOT USED ###
    # def nodeCheck(self, node):
    #     """
    #     Check if the node is available
    #     INPUT:
    #         - K8s node name (str)
    #     Return:
    #         - metric (dct)
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": ""
    #     }
    #     try:
    #         query = f'sum(irate(node_disk_read_bytes_total{{{GlobalAttrs.node_exporter_node_label}=~"{node}"}}[10m])) by ({GlobalAttrs.node_exporter_node_label}, device)'
    #         result = self.run_query(query)
    #         if not result.get('status') == 'success':
    #             output['fail_reason'] =  f"could not get metric's value: \n{query}"
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: \n{query}"
    #             return output
            
    #         devices = {}
    #         for device in result.get('data').get('result'):
    #             devices[device.get('metric').get('device')] = float(device.get('value')[1]) 

    #         output['result'] = devices
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #         Logging.log.error(e)
    #         Logging.log.exception(traceback.format_stack())

    #     return output


    def topNode(self):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            
            memory_total_query = f'node_memory_MemTotal_bytes' # f'machine_memory_bytes'
            memory_total = self.run_query(memory_total_query)
            if not memory_total.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {memory_total_query}"
                return output
            if not memory_total.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {memory_total_query}"
                return output

            memory_free_query = f'node_memory_MemFree_bytes'
            memory_free = self.run_query(memory_free_query)
            if not memory_free.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {memory_free_query}"
                return output
            if not memory_free.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {memory_free_query}"
                return output

            cpu_cores_query = f'machine_cpu_cores'
            cpu_cores = self.run_query(cpu_cores_query)
            if not cpu_cores.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {cpu_cores_query}"
                return output
            if not cpu_cores.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {cpu_cores_query}"
                return output

            cpu_used_percentage_query =  f'100 - (avg by ({GlobalAttrs.node_exporter_node_label}) (rate(node_cpu_seconds_total{{mode="idle"}}[10m])) * 100)'
            cpu_used_percentage = self.run_query(cpu_used_percentage_query)
            if not cpu_used_percentage.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {cpu_used_percentage_query}"
                return output
            if not cpu_used_percentage.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {cpu_used_percentage_query}"
                return output

            running_pods_count_query = f'kubelet_running_pods'
            running_pods_count = self.run_query(running_pods_count_query)
            if not running_pods_count.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {running_pods_count_query}"
                return output
            if not running_pods_count.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {running_pods_count_query}"
                return output

            
            nodes_dct = {}
            for node in memory_total.get('data').get('result'):
                nodes_dct[node.get('metric').get(GlobalAttrs.node_exporter_node_label)] = {
                    "memory_total": int(node.get('value')[1]),
                    "memory_free": -1,
                    "memory_used": -1,
                    "cpu_cores": -1,
                    # "cpu_used": -1, # not sure of the metrics to get the used cpu in milicores.
                    "cpu_used_percentage": -1,
                    "running_pods_num": -1,
                }
            
            for node in memory_free.get('data').get('result'):
                nodes_dct[node.get('metric').get(GlobalAttrs.node_exporter_node_label)]['memory_free'] = int(node.get('value')[1])
                nodes_dct[node.get('metric').get(GlobalAttrs.node_exporter_node_label)]['memory_used'] = nodes_dct[node.get('metric').get(GlobalAttrs.node_exporter_node_label)]['memory_total'] - int(node.get('value')[1])

            for node in cpu_cores.get('data').get('result'):
                try:
                    nodes_dct[node.get('metric').get('instance')]['cpu_cores'] = int(node.get('value')[1])
                except KeyError:
                    pass # A KeyError Exception is expected as this metric returns the value for the master nodes while other metrics dont.

            for node in cpu_used_percentage.get('data').get('result'):
                nodes_dct[node.get('metric').get(GlobalAttrs.node_exporter_node_label)]['cpu_used_percentage'] = float(node.get('value')[1])

            for node in running_pods_count.get('data').get('result'):
                try:
                    nodes_dct[node.get('metric').get('instance')]['running_pods_num'] = int(node.get('value')[1])
                except KeyError:
                    pass # A KeyError Exception is expected as this metric returns the value for the master nodes while other metrics dont.

            output['result'] = nodes_dct
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output


    def topNodeTable(self):
        """
        """
        nodes_json = self.topNode()
        # import rich
        # rich.print(nodes_json)
        if not nodes_json.get('success'):
            print(f"No nodes found \n{bcolors.WARNING + str(nodes_json.get('fail_reason')) + bcolors.ENDC}")
            exit(1)


        table = [['NODE', 'MEM TOTAL', 'MEM USAGE', 'MEM FREE', 'CPU CORES', 'CPU USAGE%', 'RUNNING PODS' ]]
        for  node, value in nodes_json.get('result').items():
            row = [node, helper_.bytes_to_kb_mb_gb(value.get('memory_total')), helper_.bytes_to_kb_mb_gb(value.get('memory_used')), helper_.bytes_to_kb_mb_gb(value.get('memory_free')), value.get('cpu_cores'), str(round(value.get('cpu_used_percentage'))) + "%", value.get('running_pods_num')]
            table.append(row)
        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
        print(out)
        


        



