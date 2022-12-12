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
- [x] Live monitoring for a Node [ 95% done ]
- [x] Live monitoring for a Pod / Containers [ 60% done ]
- [ ] top pods & nodes
    - [ ] sort by: memory_usage, cpu_usage, fs_usage
- [ ] top pvcs


<br>

---

<br>

## Installation [not ready]

> Compatible with Python 3.6+

```bash
pip3 install kptop --upgrade
```

### To use it as a Kubectl argument

`vi ~/.bash_rc`

```bash
# 
```




---

<br>

## Examples


### Live monitoring for Nodes

```
kptop node <NODE>
```


<br>

### Live monitoring for Pods

```
kptop pod <POD>
```


<br>

### Live monitoring for Containers

```
kptop pod <POD> --container <CONTAINER>
```

<br>





