from kubePtop.session import PrometheusAPI
from kubePtop.global_attrs import GlobalAttrs
from kubePtop.logging import Logging
from kubePtop.helper import Helper
from kubePtop.colors import Bcolors
bcolors = Bcolors()
helper_ = Helper()
from tabulate import tabulate
import textwrap
# import rich
import math
import traceback

class PrometheusPodsMetrics(PrometheusAPI):
    def __init__(self):
        super().__init__()


    def podExists(self, pod, namespace="default"):
        """
        Check if the pod exists
        Returns (Bolean) True if yes, False if no
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": False
        }
        try:
            query = f'sum(container_last_seen{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: \n{query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = True
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output



    def podMetrics(self, pod, node=".*", container=".*", namespace="default"):
        output = {}
        
        output['cpu'] = {
            'cpuLoadAvg10s': self.podCpuLoadAvg_10s(pod, node, container, namespace),
            'cpuUsageAVG10mMilicores': self.podCpuUsageAvg_10m(pod, node, container, namespace),
            'cpuUsageSystemAVG10mMilicores': self.podCpuUsageSystemAvg_10m(pod, node, container, namespace),
            'cpuUsageUserAVG10mMilicores': self.podCpuUsageUserAvg_10m(pod, node, container, namespace),
            'cpuQuotaMilicores': self.podCpuLimit(pod, node, container, namespace),
        }

        output['memory'] = {
            'MemLimitBytes': self.podMemLimit(pod, node, container, namespace), # total,
            'MemCachedBytes': self.podMemCache(pod, node, container, namespace),
            'MemUsageBytes': self.podMemUsage(pod, node, container, namespace),
            'MemUsageMaxBytes': self.podMemUsageMax(pod, node, container, namespace),
        }

        return output

    def podMemUsage(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                # Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                # Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podMemUsagePerContainers(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes (per container)
        Sample Return:
            {'success': True, 'fail_reason': '', 'result': {'cp-kafka-broker': 18870292480.0, 'prometheus-jmx-exporter': 212209664.0}}
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = f'sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            for container in result.get('data').get('result'):
                output['result'][container.get('metric').get('container')] = float(container.get('value')[1])

            output['success'] = True
            

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podMemUsagePerContainers_range(self, pod=".*", node=".*", container=".*", namespace="default", range_="3h"):
        """
        Return Pod memory usage in bytes (per container)
        Sample Return:
        -> Returns the data in Megabytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": []
        }
        try:
            query = f'container_memory_working_set_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{range_}]'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            # for container in result.get('data').get('result'):
            #     output['result'][container.get('metric').get('container')] = container.get('value')[1]
            
            # output['result'] = result.get('data').get('result')[0].get('values')
            timestamp_value = result.get('data').get('result')[0].get('values')
            for i in timestamp_value:
                output['result'].append(round(helper_.bytes_to_mb(float(i[1]))))

            output['success'] = True
            
        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podMemUsageMax(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_max_usage_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podMemLimit(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_memory_limit_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podMemCache(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_cache{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output
        

    def podSwapLimit(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_memory_swap_limit_bytes{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podCpuLoadAvg_10s(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_cpu_load_average_10s{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podCpuUsageAvg_10m(self, pod=".*", node=".*", container=".*", namespace="default", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(container_cpu_usage_seconds_total{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = math.ceil(float(result.get('data').get('result')[0].get('value')[1]))
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podCpuUsageSystemAvg_10m(self, pod=".*", node=".*", container=".*", namespace="default", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(container_cpu_system_seconds_total{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = math.ceil(float(result.get('data').get('result')[0].get('value')[1]))
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podCpuUsageUserAvg_10m(self, pod=".*", node=".*", container=".*", namespace="default", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(irate(container_cpu_user_seconds_total{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output
            
            output['result'] = math.ceil(float(result.get('data').get('result')[0].get('value')[1]))
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podCpuLimit(self, pod=".*", node=".*", container=".*", namespace="default"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_cpu_quota{{image!="", container!="", container!="POD", namespace=~"{namespace}", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            result = int(result.get('data').get('result')[0].get('value')[1])
            if result > 0:
                result = result // 10
                result = result // 10
            output['result'] = result
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podPVC(self, pod=".*", namespace="default"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            # Get PVCs Names used by the Pod.
            pvcs_names_query = f'sum(kube_pod_spec_volumes_persistentvolumeclaims_info{{namespace=~"{namespace}", pod=~"{pod}", container=~".*"}}) by (namespace, persistentvolumeclaim, volume, pod)'
            pvc_names_result = self.run_query(pvcs_names_query)
            if not pvc_names_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_names_query}"
                return output
            if not pvc_names_result.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {pvcs_names_query}"
                return output

            pvcs_dct = {}
            for pvc in pvc_names_result.get('data').get('result'):
                pvcs_dct[pvc.get('metric').get('persistentvolumeclaim')] = {
                    "namespace": pvc.get('metric').get('namespace'),
                    "pod": pvc.get('metric').get('pod'),
                    "volume": pvc.get('metric').get('volume'),
                    "capacity": -1,
                    "used": -1,
                    "available": -1,
                }
            
            for pvc in pvcs_dct.keys():
                
                # Get PVCs capacity
                pvcs_capacity_query = f'sum(kubelet_volume_stats_capacity_bytes{{persistentvolumeclaim=~"{pvc}"}}) by (persistentvolumeclaim, namespace)'
                pvcs_names_result = self.run_query(pvcs_capacity_query)
                if not pvcs_names_result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric's value: {pvcs_capacity_query}"
                    return output
                if not pvcs_names_result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data: {pvcs_capacity_query}"
                    # return output
                if pvcs_names_result.get('data').get('result'):
                    pvcs_dct[pvc]['capacity'] = int(pvcs_names_result.get('data').get('result')[0].get('value')[1])

                # Get PVCs used
                pvcs_used_query = f'sum(kubelet_volume_stats_used_bytes{{persistentvolumeclaim=~"{pvc}"}}) by (persistentvolumeclaim, namespace)'
                pvcs_used_result = self.run_query(pvcs_used_query)
                if not pvcs_used_result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric's value: {pvcs_used_query}"
                    return output
                if not pvcs_used_result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data: {pvcs_used_query}"
                    # return output
                if pvcs_used_result.get('data').get('result'):
                    pvcs_dct[pvc]['used'] = int(pvcs_used_result.get('data').get('result')[0].get('value')[1])

                # Get PVCs used
                pvcs_available_query = f'sum(kubelet_volume_stats_available_bytes{{persistentvolumeclaim=~"{pvc}"}}) by (persistentvolumeclaim, namespace)'
                pvcs_available_result = self.run_query(pvcs_available_query)
                if not pvcs_available_result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric's value: {pvcs_available_query}"
                    return output
                if not pvcs_available_result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data: {pvcs_available_query}"
                    # return output
                if pvcs_available_result.get('data').get('result'):
                    pvcs_dct[pvc]['available'] = int(pvcs_available_result.get('data').get('result')[0].get('value')[1])
   
            output['result'] = pvcs_dct
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podNetworkReceiveBytes(self, pod=".*", namespace="default"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = f'sum(irate(container_network_receive_bytes_total{{container!="", namespace=~"{namespace}", pod=~"{pod}"}}[10m])) by (pod, instance, namespace, interface)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 
            
            output['result'] = interfaces
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podNetworkTransmitBytes(self, pod=".*", namespace="default"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            query = f'sum(irate(container_network_transmit_bytes_total{{container!="", namespace=~"{namespace}", pod=~"{pod}"}}[10m])) by (pod, instance, namespace, interface)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = interfaces
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output
        

    def podPVC_table(self, pod, namespace="default"):
        """
        """
        pod_pvcs_dct = self.podPVC(pod, namespace)
        if not pod_pvcs_dct.get('success'):
            return " " # pod_pvcs_dct.get('fail_reason')
        
        if len(pod_pvcs_dct.get('result')) < 1:
            return "No PVCs used by the pod"

        table = [['PVC', 'CAPACITY', 'USED', 'AVAILABLE']]
        for pvc, value in pod_pvcs_dct.get('result').items():
            pvc_name = "\n".join(textwrap.wrap(pvc, width=23, replace_whitespace=False))

            if value.get('capacity') != -1:
                capacity = helper_.bytes_to_kb_mb_gb(value.get('capacity'))
            else:
                capacity = "?"

            if value.get('used') != -1:
                used = helper_.bytes_to_kb_mb_gb(value.get('used'))
            else:
                used = "?"

            if value.get('available') != -1:
                available = helper_.bytes_to_kb_mb_gb(value.get('available'))
            else:
                available = "?"

            row = [pvc_name, capacity, used, available]
            table.append(row)
        
        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
        return out

    def podUpTime(self, pod=".*", namespace="default", container=".*"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": 0
        }
        try:
            query = f'sum(time() - container_start_time_seconds{{pod="{pod}", container=~"{container}", namespace=~"{namespace}", container!="POD", image!=""}}) by (pod, instance, namespace, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podFileDescriptors(self, pod=".*", namespace="default", container=".*"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": 0
        }
        try:
            query = f'sum(container_file_descriptors{{pod="{pod}", container=~"{container}", namespace=~"{namespace}", container!="POD", image!=""}}) by (pod, instance, namespace, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podThreads(self, pod=".*", namespace="default", container=".*"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": 0
        }
        try:
            query = f'sum(container_threads{{pod="{pod}", container=~"{container}", namespace=~"{namespace}", container!="POD", image!=""}}) by (pod, instance, namespace, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output

    def podProcesses(self, pod=".*", namespace="default", container=".*"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": 0
        }
        try:
            query = f'sum(container_processes{{pod="{pod}", container=~"{container}", namespace=~"{namespace}", container!="POD", image!=""}}) by (pod, instance, namespace, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podStartTime(self, pod=".*", namespace="default", container=".*"):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": 0
        }
        try:
            query = f'sum(container_start_time_seconds{{pod="{pod}", container!="POD", image!="", namespace=~"{namespace}", container=~"{container}"}}) by (pod, namespace, device, container)'
            result = self.run_query(query)

            if not result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {query}"
                Logging.log.error(f"could not get metric's value: {query}")
                return output

            if not result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {query}"
                Logging.log.error(f"Query did not return any data: {query}")
                return output

            interfaces = {}
            for interface in result.get('data').get('result'):
                interfaces[interface.get('metric').get('interface')] = float(interface.get('value')[1]) 

            output['result'] = float(result.get('data').get('result')[0].get('value')[1])
            
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podDiskReadBytes(self, pod, container=".*", namespace="default"):
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
            query = f'sum(irate(container_fs_reads_bytes_total{{pod="{pod}", namespace=~"{namespace}", container=~"{container}"}}[10m])) by (pod, namespace, device)'
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

    def podDiskWriteBytes(self, pod, container=".*", namespace="default"):
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
            query = f'sum(irate(container_fs_writes_bytes_total{{pod="{pod}", namespace=~"{namespace}", container=~"{container}"}}[10m])) by (pod, namespace, device)'
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

    def topPod(self, namespace="default", sort_by_mem_usage=False):
        """
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }

        try:
            memory_limit_query = f'sum(container_spec_memory_limit_bytes{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}) by (pod, instance, namespace)'

            memory_usage_query = f'sum(container_memory_working_set_bytes{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}) by (pod, instance, namespace)'
            if sort_by_mem_usage:
                memory_usage_query = f'sort_desc(sum(container_memory_working_set_bytes{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}) by (pod, instance, namespace))'
                
            memory_usage_max_query = f'sum(container_memory_max_usage_bytes{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}) by (pod, instance, namespace)'
            cpu_limit_query = f'sum(container_spec_cpu_quota{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}) by (pod, instance, namespace)'
            cpu_usage_query = f'sum(irate(container_cpu_usage_seconds_total{{namespace=~"{namespace}", image!="", container!="", container!="POD"}}[10m])) by (pod, instance, namespace)'

            memory_limit = self.run_query(memory_limit_query)
            if not memory_limit.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{memory_limit_query}"
                return output

            # if not memory_limit.get('data').get('result'):
            #     output['fail_reason'] = f"Query did not return any data: \n{memory_limit_query}"
            #     return output

            memory_usage = self.run_query(memory_usage_query)
            if not memory_usage.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{memory_usage_query}"
                return output

            if not memory_usage.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{memory_usage_query}"
                return output

            memory_usage_max = self.run_query(memory_usage_max_query)
            if not memory_usage_max.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{memory_usage_max_query}"
                return output

            if not memory_usage_max.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{memory_usage_max_query}"
                return output

            cpu_limit = self.run_query(cpu_limit_query)
            if not cpu_limit.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{cpu_limit_query}"
                return output

            # if not cpu_limit.get('data').get('result'):
            #     output['fail_reason'] = f"Query did not return any data: \n{cpu_limit_query}"
            #     return output

            cpu_usage = self.run_query(cpu_usage_query)
            if not cpu_usage.get('status') == 'success':
                output['fail_reason'] = f"could not get metric value: \n{cpu_usage_query}"
                return output

            if not cpu_usage.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: \n{cpu_usage_query}"
                return output

            dct = {}
            if (len(memory_usage.get('data').get('result')) > 0) and (len(memory_limit.get('data').get('result')) > 0) and (len(memory_usage.get('data').get('result')) > 0):
                for pod_mem_usage in memory_usage.get('data').get('result'):
                    dct[pod_mem_usage.get('metric').get('pod')] = {
                        "namespace": pod_mem_usage.get('metric').get('namespace'),
                        "instance": pod_mem_usage.get('metric').get('instance'),
                        "memory_usage": int(pod_mem_usage.get('value')[1]),
                        "memory_usage_max": 0,
                        "memory_limit": 0,
                        "cpu_limit": 0
                    }
                for pod_mem_limit in memory_limit.get('data').get('result'):
                    dct[pod_mem_limit.get('metric').get('pod')]["memory_limit"] = int(pod_mem_limit.get('value')[1])             
            
                for pod_mem_usage_max in memory_usage_max.get('data').get('result'):
                    dct[pod_mem_usage_max.get('metric').get('pod')]["memory_usage_max"] = int(pod_mem_usage_max.get('value')[1])

                for pod_cpu_limit in cpu_limit.get('data').get('result'):
                    dct[pod_cpu_limit.get('metric').get('pod')]["cpu_limit"] = int(pod_cpu_limit.get('value')[1][:-2])

                for pod_cpu_usage in cpu_usage.get('data').get('result'):
                    dct[pod_cpu_usage.get('metric').get('pod')]["cpu_usage"] = float('%.2f' % float(pod_cpu_usage.get('value')[1]))


            output['result'] = dct
            output['success'] = True

        except(KeyError, AttributeError) as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())

        return output


    def topPodTable(self, namespace="default", sort_by_mem_usage=False):
        """
        """
        pods_json = self.topPod(namespace=namespace, sort_by_mem_usage=sort_by_mem_usage)
        if not pods_json.get('success'):
            print(f"No pods found in the '{namespace}' namespace \n{bcolors.WARNING + pods_json.get('fail_reason') + bcolors.ENDC}")
            exit(1)
        # import rich
        # rich.print_json(data=pods_json)

        table = [['NAMESPACE', 'POD', 'MEM LIMIT', 'MEM USAGE', 'MEM USAGE%', 'MEM USAGE MAX', 'MEM FREE', 'CPU LIMIT', 'CPU USAGE' ]]
        for pod, value in pods_json.get('result').items():
            
            # pvc_name = "\n".join(textwrap.wrap(pvc, width=23, replace_whitespace=False))

            if int(value.get('memory_limit')) == 0:
                memory_limit = "---" #"NO_LIMIT"
                memory_free = "---"
                memory_usage_percentage = "---"
            else:
                memory_limit = helper_.bytes_to_kb_mb_gb(value.get('memory_limit'))
                memory_free = helper_.bytes_to_kb_mb_gb(value.get('memory_limit') - value.get('memory_usage'))
                memory_usage_percentage = helper_.percentage(value.get('memory_usage'), value.get('memory_limit'))

            if int(value.get('cpu_limit')) == 0:
                cpu_limit = "---" #"NO_LIMIT"
                cpu_usage = ""

            else:
                cpu_limit = str(value.get('cpu_limit')) + "m"


            row = [value.get('namespace'), pod, memory_limit, helper_.bytes_to_kb_mb_gb(value.get('memory_usage')), memory_usage_percentage, helper_.bytes_to_kb_mb_gb(value.get('memory_usage_max')), memory_free, cpu_limit, str(value.get('cpu_usage')) + "m"]
            table.append(row)
        
        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
        print(out)


    def topPvc(self, pod=".*", namespace="default"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": {}
        }
        try:
            # Get PVCs Names used by the Pod.
            pvcs_names_query = f'sum(kube_pod_spec_volumes_persistentvolumeclaims_info{{namespace=~"{namespace}", pod=~"{pod}", container=~".*"}}) by (namespace, persistentvolumeclaim, volume, pod)'
            pvc_names_result = self.run_query(pvcs_names_query)
            if not pvc_names_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_names_query}"
                return output
            if not pvc_names_result.get('data').get('result'):
                output['fail_reason'] =  f"Query did not return any data: {pvcs_names_query}"
                return output

            pvcs_dct = {}
            for pvc in pvc_names_result.get('data').get('result'):
                pvcs_dct[pvc.get('metric').get('persistentvolumeclaim')] = {
                    "namespace": pvc.get('metric').get('namespace'),
                    "pod": pvc.get('metric').get('pod'),
                    "volume": pvc.get('metric').get('volume'),
                    "capacity": -1,
                    "used": -1,
                    "available": -1,
                }


            # Get PVCs capacity
            pvcs_capacity_query = f'sum(kubelet_volume_stats_capacity_bytes{{namespace=~"{namespace}", persistentvolumeclaim=~".*"}}) by (persistentvolumeclaim, namespace)'
            pvcs_capacity_result = self.run_query(pvcs_capacity_query)
            # import rich
            # rich.print(pvcs_capacity_result)
            # exit(1)
            if not pvcs_capacity_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_capacity_query}"
                return output
            if not pvcs_capacity_result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {pvcs_capacity_query}"
                # return output
            if pvcs_capacity_result.get('data').get('result'):
                for pvc_json in pvcs_capacity_result.get('data').get('result'):
                    pvcs_dct[pvc_json.get('metric').get('persistentvolumeclaim')]['capacity'] = int(pvc_json.get('value')[1])
            

            # Get PVCs used
            pvcs_used_query = f'sum(kubelet_volume_stats_used_bytes{{namespace=~"{namespace}", persistentvolumeclaim=~".*"}}) by (persistentvolumeclaim, namespace)'
            pvcs_used_result = self.run_query(pvcs_used_query)
            if not pvcs_used_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_used_query}"
                return output
            if not pvcs_used_result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {pvcs_used_query}"
                # return output
            if pvcs_used_result.get('data').get('result'):
                for pvc_json in pvcs_used_result.get('data').get('result'):
                    pvcs_dct[pvc_json.get('metric').get('persistentvolumeclaim')]['used'] = int(pvc_json.get('value')[1])

            # Get PVCs available
            pvcs_available_query = f'sum(kubelet_volume_stats_available_bytes{{namespace=~"{namespace}", persistentvolumeclaim=~".*"}}) by (persistentvolumeclaim, namespace)'
            pvcs_available_result = self.run_query(pvcs_available_query)
            if not pvcs_available_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_available_query}"
                return output
            if not pvcs_available_result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {pvcs_available_query}"
                # return output
            if pvcs_available_result.get('data').get('result'):
                for pvc_json in pvcs_available_result.get('data').get('result'):
                    pvcs_dct[pvc_json.get('metric').get('persistentvolumeclaim')]['available'] = int(pvc_json.get('value')[1])

            output['result'] = pvcs_dct
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def topPvcTable(self, namespace="default"):
        """
        """
        pvc_json = self.topPvc(namespace=namespace)
        # import rich
        # rich.print_json(data=pvc_json)
        if not pvc_json.get('success'):
            print(f"No pvc's found in the '{namespace}' namespace \n{bcolors.WARNING + str(pvc_json.get('fail_reason')  ) + bcolors.ENDC}")
            exit(1)

        table = [['NAMESPACE', 'PVC', 'VOLUME', 'CAPACITY', 'USED', 'USED%', 'FREE', 'FREE%' ]]
        for pvc, value in pvc_json.get('result').items():

            if value.get('capacity') != -1:
                capacity = helper_.bytes_to_kb_mb_gb(value.get('capacity'))
            else:
                capacity = "?"

            if value.get('used') != -1:
                used = helper_.bytes_to_kb_mb_gb(value.get('used'))
                used_percentage = helper_.percentage(value.get('used'), value.get('capacity'))
            else:
                used = "?"
                used_percentage = "?"

            if value.get('available') != -1:
                available = helper_.bytes_to_kb_mb_gb(value.get('available'))
                available_percentage = helper_.percentage(value.get('available'), value.get('capacity'))
            else:
                available = "?"
                available_percentage = "?"

            row = [value.get('namespace'), pvc, value.get('volume'), capacity, used, used_percentage, available, available_percentage]
            table.append(row)
        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
        print(out)

