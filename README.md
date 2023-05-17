# Kube-Prometheus-Top [ kptop ]

A Python tool that provides Monitoring for Kubernetes Nodes, Pods, Containers, and PVCs resources on the terminal through Prometheus metircs


https://user-images.githubusercontent.com/33789516/208325820-27111e21-81cb-446d-a5a4-0d73a615ea70.mp4



<br>

## Motivation

The resources metrics provided by the K8s APIs are very limited compared what what's scraped by Prometheus.

This tool is using Prometheus as a data source for metrics to display all the needed informations right on the terminal.

<br>

## Project Status
<br>

- [x] [Top Nodes](#top_nodes)
   - [x] [-o cloud  //  -o json](#top_nodes_option)
- [x] [Live monitoring for Nodes](#monitor_node)
- [x] [Top Pods](#top_pods)
- [x] [Live monitoring for Pods/Containers](#monitor_pod)
- [x] [Top PVCs](#top_pvcs)

> Additional

- [x] [Check the connection with Prometheus Server](#verify_prometheus)
- [x] [Check the existence of the needed Prometheus metrics](#check_metrics) <sub>[ [good for similar use cases](https://github.com/eslam-gomaa/kptop/issues/15) ]</sub>

<br>

---

<br>

## Installation
<a id=installation></a>

> Compatible with Python 3.6+

[on PyPi](https://pypi.org/project/kptop)

```bash
pip3 install kptop --upgrade
```


<br>

---

## Environment Variables
<a id=env></a>

| ENV | Description                                                                          | Default | Required |
| ----- | -------------------------------------------------------------------------------------- | --------- | ---------- |
| `KPTOP_CONNECTION_METHOD`    | The way to connect to Prometheus server<br />**options:** ['prometheus_endpoint', 'pod_portForward'] | <br />      | Yes      |

There are 2 options to connect KPtop to Prometheus:
1. With a Prometheus server endpoint
    - Suitable if Prometheus is exposed (with an ingress for example)
2. With 'K8s pod port-forward' (Through K8s API-Server)
    - Suitable if Prometheus is Not exposed (Only rechable within the K8s cluster)


#### `prometheus_endpoint` ENVs

| ENV | Description                                                     | Default | Required |
| ----- | ----------------------------------------------------------------- | --------- | ---------- |
| `KPTOP_PROMETHEUS_SERVER`    | Prometheus server URL                                           |         | Yes      |
| `KPTOP_BASIC_AUTH_ENABLED`    | Whether basic authentication is needed to connect to Prometheus | False   | No       |
| `KPTOP_PROMETHEUS_USERNAME`    | Prometheus username                                             |         | No       |
| `KPTOP_PROMETHEUS_PASSWORD`    | Prometheus password                                             |         | No       |
| `KPTOP_INSECURE`    | Verify SSL certificate                                          | False   | No       |


<br>

#### `pod_portForward` ENVs

| ENV | Description                                            | Default | Required |
| ----- | -------------------------------------------------------- | --------- | ---------- |
| `KPTOP_PROMETHEUS_POD_NAME`    | Prometheus pod name                                    |         | Yes      |
| `KPTOP_PROMETHEUS_POD_PORT`    | Prometheus port number                                 | 9090    | No       |
| `KPTOP_PROMETHEUS_POD_NAMESPACE`    | The name space in which the Prometheus pod is deployed | default | No       |
| `KUBECONFIG`    | custom K8s kube config file                            | *default path*        | No       |


<br>

#### General ENVs


| ENV | Description                                                            | Default | Required |
| ----- | ------------------------------------------------------------------------ | --------- | ---------- |
| `KPTOP_NODE_EXPORTER_NODE_LABEL`    | node exporter "node label"                                             | "node"  | NO       |
| `KPTOP_START_GRAPHS_WITH_ZERO`    | By default graphs begin with '0'  to let the graph take its full hight | True    | NO       |
| `KPTOP_LOGGING_DIR`    | Choose a different logging directory                                   | /tmp/   | NO       |
| `KPTOP_GRAPH_WIDTH`    | Choose a custom graphs width                                           | 45      | NO       |


<br>

## CLI Arguments
<a id=cli></a>


| ENV                          | Description                                                  | Default                                                      |
| ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `--namespace`,  `-n`         | Specify a Kubernetes Namespace                               | default                                                      |
| `--all-namespaces`,  -A      |                                                              |                                                              |
| `--container`,  `-c`         | Specify a container                                          |                                                              |
| `--interval`,  `-i`          | Live monitoring update interval                              | 8  <br> <sub>[**NOTE**: the actuall update depends on the Prometheus scaping interval (15s by default)]</sub> |
| `--debug`,  `-d`             | Enable debugging logging mode                                | False                                                        |
| `--verify-prometheus`,  `-V` | Verify connectivity to Prometheus server & check the existence of the needed exporters |                                                              |
| `--sort-by-mem-usage`,  `-s` | Sort top result by memory usage                              | False                                                        |
| `--check-metrics` ,  `-C`    | Check the existence of the needed metrics, _needs to be done with_  `-V` | False                                                        |

<br>

---

<br>

## Usage


<br>

Add the ENVs and you're good to go.

_*Examples*_

```bash
export KPTOP_CONNECTION_METHOD="pod_portForward"
export KPTOP_PROMETHEUS_POD_NAME="my-prometheus-server-0"
export KPTOP_PROMETHEUS_POD_PORT="9090"
export KPTOP_PROMETHEUS_POD_NAMESPACE="monitoring"
```

> Or

```bash
export KPTOP_CONNECTION_METHOD="prometheus_endpoint"
export KPTOP_PROMETHEUS_SERVER="http://prometheus.home-lab.com"
```

<br>

### Top nodes 
<a id=top_nodes></a>

```bash
kptop nodes
```

```bash
NODE      MEM TOTAL    MEM USAGE    MEM FREE      CPU CORES  CPU USAGE%      RUNNING PODS
worker-1  19.6 gb      16.92 gb     2.69 gb               6  9%                        14
worker-2  19.6 gb      9.52 gb      10.08 gb              6  9%                        27
```


**[kptop nodes --option / -o](https://github.com/eslam-gomaa/kptop/releases/tag/v0.0.6) 🎉**
<a id=top_nodes_option></a>


```bash
kptop nodes -o json --colorize-json
```

> Under testing (currently tested with EKS)

```bash
kptop nodes -o cloud
```


<br>


### Live monitoring for Nodes
<a id=monitor_node></a>

```bash
kptop node <NODE>
```


![image](https://user-images.githubusercontent.com/33789516/208190533-cb719cef-e76c-4c6d-8686-2f32edae15c6.png)



<br>

### Top pods
<a id=top_pods></a>

```bash
kptop pods -n <NAMESPACE>
```

```
kptop pods -n elk-stack

NAMESPACE    POD                                      MEM LIMIT    MEM USAGE    MEM USAGE %    MEM USAGE MAX    MEM FREE    CPU LIMIT    CPU USAGE
elk-stack    elasticsearch-master-0                   2.0 gb       1.38 gb      68%            2.0 gb           635.25 mb   1000m        0.04m
elk-stack    elasticsearch-master-1                   2.0 gb       1.49 gb      74%            2.0 gb           522.05 mb   1000m        0.03m
elk-stack    strimzi-filebeat-filebeat-f8ms7          200.0 mb     85.73 mb     42%            174.16 mb        114.27 mb   1000m        0.02m
elk-stack    haproxy-ingress-filebeat-filebeat-pq2wf  200.0 mb     87.73 mb     43%            171.31 mb        112.27 mb   1000m        0.03m
elk-stack    strimzi-filebeat-filebeat-r7dht          200.0 mb     119.12 mb    59%            199.52 mb        80.88 mb    1000m        0.02m
elk-stack    haproxy-ingress-filebeat-filebeat-lzqdt  200.0 mb     98.66 mb     49%            199.57 mb        101.34 mb   1000m        0.02m
elk-stack    my-kibana-kibana-79448f7fb7-wf4t6        2.0 gb       342.87 mb    16%            618.07 mb        1.67 gb     1000m        0.02m
elk-stack    my-logstash-logstash-0                   1.5 gb       1008.22 mb   65%            1.21 gb          527.78 mb   1000m        0.02m
```

```
kptop pod -n kube-system

NAMESPACE    POD                                              MEM LIMIT    MEM USAGE    MEM USAGE%    MEM USAGE MAX    MEM FREE    CPU LIMIT    CPU USAGE
kube-system  coredns-558bd4d5db-nfcjq                         170.0 mb     26.0 mb      15%           42.77 mb         144.0 mb    ---          0.0m
kube-system  coredns-558bd4d5db-vcstr                         170.0 mb     17.45 mb     10%           24.04 mb         152.55 mb   ---          0.0m
kube-system  etcd-master                                      ---          85.02 mb     ---           391.7 mb         ---         ---          0.02m
kube-system  kube-apiserver-master                            ---          635.97 mb    ---           731.13 mb        ---         ---          0.09m
kube-system  kube-controller-manager-master                   ---          95.55 mb     ---           145.41 mb        ---         ---          0.03m
kube-system  kube-proxy-q6nr7                                 ---          27.46 mb     ---           58.91 mb         ---         ---          0.0m
kube-system  kube-proxy-q489q                                 ---          21.98 mb     ---           63.0 mb          ---         ---          0.0m
kube-system  kube-proxy-bghp6                                 ---          22.35 mb     ---           64.1 mb          ---         ---          0.0m
kube-system  kube-scheduler-master                            ---          37.04 mb     ---           61.68 mb         ---         ---          0.0m
kube-system  nfs-subdir-external-provisioner-b97f4d9f5-bjp2h  ---          9.43 mb      ---           37.48 mb         ---         ---          0.0m
```


<br>

### Live monitoring for Pods
<a id=monitor_pod></a>

```bash
kptop pod <POD> -n <NAMESPACE>
```

![image](https://user-images.githubusercontent.com/33789516/208233405-f07bab04-896e-4d80-bed5-f92deae91e19.png)  

![image](https://user-images.githubusercontent.com/33789516/208233544-e51e1ec2-a4c9-4615-9f9f-32156937a18c.png)

![image](https://user-images.githubusercontent.com/33789516/208233652-ed26534f-f5f1-486f-a3df-87800ebc8b73.png)

![image](https://user-images.githubusercontent.com/33789516/208233865-9026acfa-ad64-475a-8337-8e8edab1fcb9.png)



<br>

### Live monitoring for Containers
<a id=monitor_container></a>

```bash
kptop pod <POD> -n <NAMESPACE> -c <CONTAINER>
```

![image](https://user-images.githubusercontent.com/33789516/208234009-e3656b8b-6fdb-4f72-bb87-15332c67e3d7.png)



<br>

### Top PVCs
<a id=top_pvcs></a>


```bash
kptop pvcs <NAMESPACE>
```
 
> **NOTE:** in this example, all VPCs have the same capacity because this is a testing environment (using [nfs-provisioner](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner))


```bash
kptop pvcs --all-namespaces
```

```
NAMESPACE    PVC                                          VOLUME                CAPACITY    USED      USED %    FREE      FREE %
elk-stack    elasticsearch-master-elasticsearch-master-0  elasticsearch-master  123.14 gb   21.42 gb  17%       95.43 gb  77%
elk-stack    elasticsearch-master-elasticsearch-master-1  elasticsearch-master  123.14 gb   21.42 gb  17%       95.43 gb  77%
elk-stack    elasticsearch-master-elasticsearch-master-2  elasticsearch-master  ?           ?         ?         ?         ?
kafka        data-0-kafka-cluster-region1-kafka-0         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-0-kafka-cluster-region1-kafka-1         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-0-kafka-cluster-region1-kafka-2         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-0-kafka-cluster-region2-kafka-0         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-0-kafka-cluster-region2-kafka-1         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-0-kafka-cluster-region2-kafka-2         data-0                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-1-kafka-cluster-region1-kafka-0         data-1                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-1-kafka-cluster-region1-kafka-1         data-1                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-1-kafka-cluster-region1-kafka-2         data-1                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-2-kafka-cluster-region1-kafka-0         data-2                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-2-kafka-cluster-region1-kafka-1         data-2                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-2-kafka-cluster-region1-kafka-2         data-2                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-3-kafka-cluster-region1-kafka-0         data-3                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-3-kafka-cluster-region1-kafka-1         data-3                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-3-kafka-cluster-region1-kafka-2         data-3                123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-kafka-cluster-region1-zookeeper-0       data                  123.14 gb   21.42 gb  17%       95.43 gb  77%
kafka        data-kafka-cluster-region2-zookeeper-0       data                  123.14 gb   21.42 gb  17%       95.43 gb  77%
prometheus   my-prometheus-alertmanager                   storage-volume        123.14 gb   21.42 gb  17%       95.43 gb  77%
prometheus   my-prometheus-server                         storage-volume        123.14 gb   21.42 gb  17%       95.43 gb  77%
```


<br>


### Verify Prometheus connectivity
<a id=verify_prometheus></a>

```bash
kptop --verify-prometheus
```

<details>
    <summary>
        <b style="font-size:14px" >Sample output</b>
    </summary>
    <br>

```bash 
Verifying Prometheus connection: Connected                     
{
  "connected": true,
  "status_code": 200,
  "reason": "",
  "fail_reason": ""
}

Verifying Prometheus Exporters:

* Node Exporter:  Found             
{
  "success": true,
  "fail_reason": "",
  "result": {
    "found_versions": {
      "1.3.1": "2"
    }
  }
}

* Kubernetes Exporter:  Found           
{
  "success": true,
  "fail_reason": "",
  "result": {
    "found_git_versions": {
      "v1.21.0": "3",
      "v1.21.14": "1"
    }
  }
}
```
    
</details>


<br>

---

### Check Prometheus metrics
<a id=check_metrics></a>


```bash
kptop --verify-prometheus --check-metrics
```


<details>
    <summary>
        <b style="font-size:14px" >Sample output</b>
    </summary>
    <br>

```bash 
Verifying Prometheus connection: Connected                     
{
  "connected": true,
  "status_code": 200,
  "reason": "",
  "fail_reason": ""
}

Verifying Prometheus Exporters:

* Node Exporter:  Found             
{
  "success": true,
  "fail_reason": "",
  "result": {
    "found_versions": {
      "1.3.1": "2"
    }
  }
}

* Kubernetes Exporter:  Found           
{
  "success": true,
  "fail_reason": "",
  "result": {
    "found_git_versions": {
      "v1.21.0": "3",
      "v1.21.14": "1"
    }
  }
}
 
  0:00:00 0:00:00 Checking Metrics  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%  [ container_fs_writes_bytes_total ]
+---------------------------------------------------+---------------+-----------+-----------+
| METRIC                                            | EXPORTER      | STATE     | COMMENT   |
+===================================================+===============+===========+===========+
| node_memory_MemFree_bytes                         | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_MemAvailable_bytes                    | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_MemTotal_bytes                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_Cached_bytes                          | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_Buffers_bytes                         | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_SwapTotal_bytes                       | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_SwapFree_bytes                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_memory_SwapCached_bytes                      | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_cpu_seconds_total                            | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_load1                                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_load5                                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_load15                                       | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| machine_cpu_physical_cores                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| machine_cpu_sockets                               | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| up                                                | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_boot_time_seconds                            | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_filesystem_size_bytes                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_filesystem_avail_bytes                       | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_filesystem_avail_bytes                       | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_network_receive_bytes_total                  | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_network_transmit_bytes_total                 | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_disk_written_bytes_total                     | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| node_disk_read_bytes_total                        | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| machine_cpu_cores                                 | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| kubelet_running_pods                              | node_exporter | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_last_seen                               | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_memory_working_set_bytes                | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_memory_max_usage_bytes                  | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_spec_memory_limit_bytes                 | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_memory_cache                            | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_spec_memory_swap_limit_bytes            | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_cpu_load_average_10s                    | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_cpu_usage_seconds_total                 | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_cpu_system_seconds_total                | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_cpu_user_seconds_total                  | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_spec_cpu_quota                          | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| kube_pod_spec_volumes_persistentvolumeclaims_info | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| kubelet_volume_stats_capacity_bytes               | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| kubelet_volume_stats_used_bytes                   | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| kubelet_volume_stats_available_bytes              | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_network_receive_bytes_total             | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_network_transmit_bytes_total            | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_start_time_seconds                      | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_file_descriptors                        | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_threads                                 | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_processes                               | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_fs_reads_bytes_total                    | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_fs_writes_bytes_total                   | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
| container_fs_writes_bytes_total                   | kubernetes    | available |           |
+---------------------------------------------------+---------------+-----------+-----------+
```
    
</details>


<br>


---

<br>

## Logging

Default log file location is "`/tmp/kptop.log`"


<br>

---

<br>


## Known Issues


### 

<details>
    <summary>
        <b style="font-size:22px" > [1] Node Exporter metrics don't return data</b>
    </summary>
    <br>
    
![image](https://user-images.githubusercontent.com/33789516/208234711-bf46a36b-db60-4fba-943c-792b68f721e6.png)
    
</details>




- This is NOT an issue, the node exporter NODE label change from version to another, currently we encountered only "kubernetes_node" or "node"
- "node" is the default, to fix the it you can change it with the "[KPTOP_NODE_EXPORTER_NODE_LABEL](#env)" Environment variables

```bash
export KPTOP_NODE_EXPORTER_NODE_LABEL="node" # default
export KPTOP_NODE_EXPORTER_NODE_LABEL="kubernetes_node"
```

> auto detection of exporters verstions can be implemented later (if needed).

<br>

---



<br>

Reach me anytime on [Linkedin](https://www.linkedin.com/in/eslam-gomaa/)

