from kubePtop.session import PrometheusAPI
from kubePtop.global_attrs import GlobalAttrs
from kubePtop.logging import Logging
from kubePtop.helper import Helper
helper_ = Helper()
from tabulate import tabulate
import textwrap
import rich
import math
import traceback

class PrometheusPodsMetrics(PrometheusAPI):
    def __init__(self):
        super().__init__()

    def podMetrics(self, pod, node=".*", container=".*"):
        output = {}
        
        output['cpu'] = {
            'cpuLoadAvg10s': self.podCpuLoadAvg_10s(pod, node, container),
            'cpuUsageAVG10mMilicores': self.podCpuUsageAvg_10m(pod, node, container),
            'cpuUsageSystemAVG10mMilicores': self.podCpuUsageSystemAvg_10m(pod, node, container),
            'cpuUsageUserAVG10mMilicores': self.podCpuUsageUserAvg_10m(pod, node, container),
            'cpuQuotaMilicores': self.podCpuLimit(pod, node, container),
        }

        output['memory'] = {
            'MemLimitBytes': self.podMemLimit(pod, node, container), # total,
            'MemCachedBytes': self.podMemCache(pod, node, container),
            'MemUsageBytes': self.podMemUsage(pod, node, container),
            'MemUsageMaxBytes': self.podMemUsageMax(pod, node, container),
        }

        return output

    def podMemUsage(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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

    def podMemUsagePerContainers(self, pod=".*", node=".*", container=".*"):
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
            query = f'sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace, container)'
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

    def podMemUsageMax(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_max_usage_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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


    def podMemLimit(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_memory_limit_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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

    def podMemCache(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_memory_cache{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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
        

    def podSwapLimit(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_memory_swap_limit_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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


    def podCpuLoadAvg_10s(self, pod=".*", node=".*", container=".*"):
        """
        Return Pod memory usage in bytes
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_cpu_load_average_10s{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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

    def podCpuUsageAvg_10m(self, pod=".*", node=".*", container=".*", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(rate(container_cpu_usage_seconds_total{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
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

    def podCpuUsageSystemAvg_10m(self, pod=".*", node=".*", container=".*", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(rate(container_cpu_system_seconds_total{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
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

    def podCpuUsageUserAvg_10m(self, pod=".*", node=".*", container=".*", avg="10m"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(rate(container_cpu_user_seconds_total{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}[{avg}])) by (pod, instance, namespace)'
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

    def podCpuLimit(self, pod=".*", node=".*", container=".*"):
        """
        Return number of CPU seconds used per pods.
        """
        output = {
            "success": False,
            "fail_reason": "",
            "result": ""
        }
        try:
            query = f'sum(container_spec_cpu_quota{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
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

    def podPVC(self, pod=".*"):
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
            pvcs_names_query = f'sum(kube_pod_spec_volumes_persistentvolumeclaims_info{{pod=~"{pod}", container=~".*"}}) by (namespace, persistentvolumeclaim, volume, pod)'
            pvc_names_result = self.run_query(pvcs_names_query)
            if not pvc_names_result.get('status') == 'success':
                output['fail_reason'] = f"could not get metric's value: {pvcs_names_query}"
                return output
            if not pvc_names_result.get('data').get('result'):
                output['fail_reason'] = f"Query did not return any data: {pvcs_names_query}"
                return output

            pvcs_dct = {}
            for pvc in pvc_names_result.get('data').get('result'):
                pvcs_dct[pvc.get('metric').get('persistentvolumeclaim')] = {
                    "namespace": pvc.get('metric').get('namespace'),
                    "pod": pvc.get('metric').get('pod'),
                    "volume": pvc.get('metric').get('volume'),
                    "capacity": 0,
                    "used": 0,
                    "available": 0,
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
                    return output
                pvcs_dct[pvc]['capacity'] = int(pvcs_names_result.get('data').get('result')[0].get('value')[1])

                # Get PVCs used
                pvcs_used_query = f'sum(kubelet_volume_stats_used_bytes{{persistentvolumeclaim=~"{pvc}"}}) by (persistentvolumeclaim, namespace)'
                pvcs_used_result = self.run_query(pvcs_used_query)
                if not pvcs_used_result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric's value: {pvcs_used_query}"
                    return output
                if not pvcs_used_result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data: {pvcs_used_query}"
                    return output
                pvcs_dct[pvc]['used'] = int(pvcs_used_result.get('data').get('result')[0].get('value')[1])

                # Get PVCs used
                pvcs_available_query = f'sum(kubelet_volume_stats_available_bytes{{persistentvolumeclaim=~"{pvc}"}}) by (persistentvolumeclaim, namespace)'
                pvcs_available_result = self.run_query(pvcs_available_query)
                if not pvcs_available_result.get('status') == 'success':
                    output['fail_reason'] = f"could not get metric's value: {pvcs_available_query}"
                    return output
                if not pvcs_available_result.get('data').get('result'):
                    output['fail_reason'] = f"Query did not return any data: {pvcs_available_query}"
                    return output
                pvcs_dct[pvc]['available'] = int(pvcs_available_result.get('data').get('result')[0].get('value')[1])
   
            output['result'] = pvcs_dct
            output['success'] = True

        except Exception as e:
            output['success']: False
            output['fail_reason'] = e
            Logging.log.error(e)
            Logging.log.exception(traceback.format_stack())
        return output


    def podPVC_table(self, pod):
        """
        """
        pod_pvcs_dct = self.podPVC(pod)
        if not pod_pvcs_dct.get('success'):
            return pod_pvcs_dct.get('fail_reason')
        
        if len(pod_pvcs_dct.get('result')) < 1:
            return "No PVCs used by the pod"

        # table = [['PVC', "NAMESPACE", 'Volume', 'CAPACITY', 'USED', 'AVAILABLE']]
        table = [['PVC', 'CAPACITY', 'USED', 'AVAILABLE']]
        for pvc, value in pod_pvcs_dct.get('result').items():
            
            pvc_name = "\n".join(textwrap.wrap(pvc, width=23, replace_whitespace=False))

            row = [pvc_name, helper_.bytes_to_kb_mb_gb(value.get('capacity')), helper_.bytes_to_kb_mb_gb(value.get('used')), helper_.bytes_to_kb_mb_gb(value.get('available'))]
            table.append(row)
        
        out = tabulate(table, headers='firstrow', tablefmt='plain', showindex=False)
        return out


    # def podSwapLimit(self, pod=".*", node=".*", container=".*"):
    #     """
    #     Return Pod memory usage in bytes
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": ""
    #     }
    #     try:
    #         query = f'sum(container_spec_memory_swap_limit_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
    #         result = self.run_query(query)

    #         if not result.get('status') == 'success':
                # output['fail_reason'] = f"could not get metric's value: {query}"
                # Logging.log.error(f"could not get metric's value: {query}")
    #             return output

    #         if not result.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: {query}"
                # Logging.log.error(f"Query did not return any data: {query}")
    #             return output
            
    #         output['result'] = int(result.get('data').get('result')[0].get('value')[1]) 
    #         output['success'] = True

    #     except Exception as e:
    #         output['success']: False
    #         output['fail_reason'] = e



    
    # def PodMemUsage_(self, pod=".*", node=".*", container=".*", sort_desc=False):
    #     """
    #     Return Pod memory usage in bytes
    #     """
    #     output = {
    #         "success": False,
    #         "fail_reason": "",
    #         "result": ""
    #     }
        
    #     try:
    #         ### Memory Limit
    #         # Memory Limit is done on the pod level. (that's why I'm using 'sum')
    #         memory_limit_query = f'sum(container_spec_memory_limit_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
    #         memory_limit = self.run_query(memory_limit_query)
    #         # memory_cache = self.run_query('sum(container_memory_cache{container!="", instance="ip-192-168-104-139.me-south-1.compute.internal"}) by (pod, instance, namespace)')
    #         if not memory_limit.get('status') == 'success':
    #             output['fail_reason'] = f"could not get metric's value: {memory_usage_query}"
    #             return output

    #         if not memory_limit.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: {memory_limit_query}"
    #             return output

    #         ### Memory Usage
    #         if sort_desc:
    #             memory_usage_query = f'sort_desc(sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace))'
    #             memory_usage = self.run_query(memory_usage_query)
    #         else:
    #             memory_usage_query = f'sum(container_memory_working_set_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
    #         memory_usage = self.run_query(memory_usage_query)

    #         if not memory_usage.get('status') == 'success':
    #             output['fail_reason'] = f"could not get metric's value: {memory_usage_query}"
    #             return output

    #         if not memory_usage.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: {memory_usage_query}"
    #             return output

    #         ## Memory Usage Max
    #         memory_max_usage_query = f'sum(container_memory_max_usage_bytes{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
    #         memory_max_usage = self.run_query(memory_max_usage_query)
           
    #         if not memory_max_usage.get('status') == 'success':
    #             output['fail_reason'] = f"could not get metric's value: {memory_usage_query}"
    #             return output

    #         if not memory_max_usage.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: {memory_max_usage_query}"
    #             return output

    #         ## Memory Cache
    #         # Here ... 
    #         memory_cache_query = f'sum(container_memory_cache{{image!="", container!="", container!="POD", pod=~"{pod}", container=~"{container}", {GlobalAttrs.kubernetes_exporter_node_label}=~"{node}"}}) by (pod, instance, namespace)'
    #         memory_cache = self.run_query(memory_cache_query)
    #         if not memory_cache.get('status') == 'success':
    #             output['fail_reason'] = f"could not get metric's value: {memory_usage_query}"
    #             return output

    #         if not memory_cache.get('data').get('result'):
    #             output['fail_reason'] = f"Query did not return any data: {memory_cache_query}"
    #             return output


    #         dct = {}
    #         if len(memory_usage.get('data').get('result')) > 0 and (len(memory_limit.get('data').get('result'))) > 0:
    #             for pod_mem_usage in memory_usage.get('data').get('result'):
    #                 dct[pod_mem_usage.get('metric').get('pod')] = {
    #                     "namespace": pod_mem_usage.get('metric').get('namespace'),
    #                     "instance": pod_mem_usage.get('metric').get('instance'),
    #                     "memory_usage": int(pod_mem_usage.get('value')[1]),
    #                     "memory_usage_max": "",
    #                     "memory_limit": "",
    #                     "memory_cache": ""
    #                 }

    #             dct[pod_mem_usage.get('metric').get('pod')]["memory_limit"] = int(memory_limit.get('data').get('result')[0].get('value')[1])
    #             dct[pod_mem_usage.get('metric').get('pod')]["memory_usage_max"] = int(memory_max_usage.get('data').get('result')[0].get('value')[1])
    #             dct[pod_mem_usage.get('metric').get('pod')]["memory_cache"] = int(memory_cache.get('data').get('result')[0].get('value')[1])
                                  
            
    #         output['result'] = dct
    #         output['success'] = True

    #     except(KeyError, AttributeError) as e:
    #         output['success']: False
    #         output['fail_reason'] = e
    #     return output
