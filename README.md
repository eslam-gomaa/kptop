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
- [ ] Top nodes
- [x] Live monitoring for a Node [ 95% done ]
- [ ] Top pods
- [x] Live monitoring for a Pod / Containers [ 90% done ]
- [ ] sort by: memory_usage, cpu_usage, fs_usage
- [ ] top pvcs


<br>

---

<br>

## Installation [not ready yet]

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

| ENV                         | Description                                                  | Default | Required |
| --------------------------- | ------------------------------------------------------------ | ------- | -------- |
| KUBE_PTOP_PROMETHEUS_SERVER | Prometheus server URL                                        |         | Yes      |
| KPTOP_BASIC_AUTH_ENABLED    | Whether basic authentication is needed to connect to Prometheus | False   | No       |
| KPTOP_PROMETHEUS_USERNAME   | Prometheus username                                          |         | No       |
| KPTOP_PROMETHEUS_PASSWORD   | Prometheus password                                          |         | No       |
| KPTOP_INSECURE              | Verify SSL certificate                                       | False   | No       |





<br>

## CLI Arguments








---

<br>

## Examples

### Top nodes

```bash
kptop nodes
```

<br>


### Live monitoring for Nodes

```bash
kptop node <NODE>
```


<br>


### Top nodes

```bash
kptop pods
```

<br>

### Live monitoring for Pods

```bash
kptop pod <POD>
```


<br>

### Live monitoring for Containers

```bash
kptop pod <POD> --container <CONTAINER>
```

<br>

### Top PVCs

```bash
kptop pvcs
```

<br>




