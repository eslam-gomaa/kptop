# Kube-Prometheus-Top [ kptop ]

A Python tool that provides Monitoring for Kubernetes Nodes/Pods/Containers resources on the terminal through Prometheus metircs

<br>

## Motivation

The resources metrics provided by the K8s APIs are very limited compared what what's scraped by Prometheus
This tool is using Prometheus as a data source for metrics to display all the needed informations right on the terminal.

<br>

## Project Status
<br>

>  [[ In the Development Phase ]]
- [ ] [Top Nodes](#top_nodes)
- [x] [Live monitoring for Nodes](#monitor_node) `#done#`
- [ ] [Top Pods](#top_pods)
- [x] [Live monitoring for Pods/Containers](#monitor_pod) `#done#`
- [ ] [Top PVCs](#top_pvcs)


<br>

---

<br>

## Installation [not ready yet]
<a id=installation></a>

> Compatible with Python 3.6+

```bash
pip3 install kptop --upgrade
```

### To use it as a Kubectl argument

`vi ~/.bash_rc`

```bash
# 
```

<br>

---

## Environment Variables
<a id=env></a>

| ENV                            | Description                                                  | Default | Required |
| ------------------------------ | ------------------------------------------------------------ | ------- | -------- |
| KUBE_PTOP_PROMETHEUS_SERVER    | Prometheus server URL                                        |         | Yes      |
| KPTOP_BASIC_AUTH_ENABLED       | Whether basic authentication is needed to connect to Prometheus | False   | No       |
| KPTOP_PROMETHEUS_USERNAME      | Prometheus username                                          |         | No       |
| KPTOP_PROMETHEUS_PASSWORD      | Prometheus password                                          |         | No       |
| KPTOP_INSECURE                 | Verify SSL certificate                                       | False   | No       |
| KPTOP_NODE_EXPORTER_NODE_LABEL | node exporter "node label"                                   | "node"  | NO       |
| KPTOP_START_GRAPHS_WITH_ZERO   | By default graphs begin with '0'  to let the graph take its full hight | True    | NO       |



<br>

## CLI Arguments
<a id=cli></a>


| ENV                   | Description                     | Default |
| --------------------- | ------------------------------- | ------- |
| `--namespace`,  `-n`      | Specify a Kubernetes Namespace  | default |
| `--all-namespaces`,  `-A` |                                 |         |
| `--container`,  `-c`      | Specify a container             |         |
| `--interval`,  `-i`       | Live monitoring update interval | 8       |
| `--debug`,  `-d`          | Enable debugging logging mode   | False   |



<br>

---

<br>

## Examples

### Top nodes
<a id=top_nodes></a>

```bash
kptop nodes
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
kptop pods
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
kptop pvcs
```

<br>


---

<br>

## Known Issues


### #1 Node Exporter metrics don't return data

![image](https://user-images.githubusercontent.com/33789516/208234711-bf46a36b-db60-4fba-943c-792b68f721e6.png)


- This is NOT an issue, the node exporter NODE label change from version to another, currently we encountered only "kubernetes_node" or "node"
- "node" is sat as the default, If it doensn't work you can change it with the "[KPTOP_NODE_EXPORTER_NODE_LABEL](#env)" Environment variables

```bash
export KPTOP_NODE_EXPORTER_NODE_LABEL="node" # default
export KPTOP_NODE_EXPORTER_NODE_LABEL="kubernetes_node"
```

> auto detection of exporters verstions can be implemented later (if needed).

<br>

---










