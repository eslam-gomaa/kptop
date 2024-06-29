
# Kube-Prometheus-Top [ kptop ]

A Python tool that offers Grafana-like CLI monitoring based on Prometheus metrics, with Kubernetes integration through PodPortForward

Allowing you to create your own custom CLI dashboards & CLI commands with custom layouts, variables, CLI arguments !

<br>

# Motivation
Prometheus is widely used with different kinds of metrics - Let's make CLI monitoring more powerful with Prometheus data


<br>

---


# Installation

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
    - Suitable if Prometheus is Not exposed (Only rechable with K8s cluster access)


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

| ENV                                  | Description                                                  | Default               | Required |
| ------------------------------------ | ------------------------------------------------------------ | --------------------- | -------- |
| `KPTOP_START_GRAPHS_WITH_ZERO`       | By default graphs begin with '0'  to let the graph take its full hight | True                  | NO       |
| `KPTOP_LOGGING_DIR`                  | Choose a different logging directory                         | /tmp/                 | NO       |
| `KPTOP_GRAPH_WIDTH`                  | Choose a custom graphs width                                 | 45                    | NO       |
| `KPTOP_DEFAULT_DASHBOARDS_DIRECTORY` | Default directory contains the dashboards yaml files         | /var/kptop/dashboards | NO       |
| `KPTOP_DEFAULT_COMMANDS_DIRECTORY`   | Default directory contains the commands yaml files           | /var/kptop/commands   | NO       |



<br>

---

# CLI Arguments
<a id=cli></a>


| ENV                         | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `--dashboard` , `-D`        | Specify a dashboard YAML file                                |
| `--command` , `-C`          | Specify a command YAML file                                  |
| `--list-dashboards` , `-ld` | List all the available dashboards                            |
| `--list-commands` , `-lc`   | List all the available commands                              |
| `--debug`,  `-d`            | Enable debugging logging mode                                |
| `--version`,  `-V`          | Show kptop version                                           |
| `--print-layout`,  `-pl`    | Print the dashboard empty layout                             |
| `--vhelp` ,  `-vh`          | Print the arguments including "the variables arguments defined in your command yaml file" |


<br>

---


# Usage


## [1] Add the Prometheus connection Environment Variables

## Example

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

## [2] move your dashboards/commands to the configured directories

```
KPTOP_DEFAULT_DASHBOARDS_DIRECTORY
KPTOP_DEFAULT_COMMANDS_DIRECTORY
```

> Create / Update as required



## Run !

```bash
python kptop_tool.py --list-dashboards
```

```
DASHBOARD      CREATION TIME        UPDATE TIME
pods           29-06-2024 19:43:19  29-06-2024 19:43:19
test           29-06-2024 19:27:04  29-06-2024 19:27:04
pvcs           29-06-2024 12:33:02  29-06-2024 12:33:02
strimzi-kafka  29-06-2024 12:33:02  29-06-2024 12:33:02
```

```bash
python kptop_tool.py --dashboard pods --vhelp
```

```
usage: kptop_tool.py [-h] [--dashboard DASHBOARD] [--command COMMAND] [--list-dashboards] [--list-commands] [--vhelp] [--debug] [--print-layout] [--version] [--namespace NAMESPACE] [--pod POD]

Process some CLI arguments.

options:
  -h, --help            show this help message and exit
  --dashboard DASHBOARD, -D DASHBOARD
                        dashboard name to display
  --command COMMAND, -C COMMAND
                        command name to display
  --list-dashboards, -ld
                        List dasboards names
  --list-commands, -lc  List commands names
  --vhelp, -vh          List the variables cli arguments of the dashboard/command manifests
  --debug, -d           Debug mode
  --print-layout, -pl   Print empty layout structure
  --version, -V         Print kptop version
  --namespace NAMESPACE, -n NAMESPACE
                        Specify the namespace variable value - default: ".*"
  --pod POD, -po POD    Specify the pod variable value - default: ".*"
```

```bash
python kptop_tool.py --dashboard pods -n kafka
```
