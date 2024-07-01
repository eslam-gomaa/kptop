---
layout: default
nav_order: 2
# permalink: /
parent: Custom Dashboards
title: Dashboard Data Types
markdown: Kramdown
has_children: false
kramdown:
  parse_block_html: true
  auto_ids: true
  syntax_highlighter: coderay
---

<button class="btn js-toggle-dark-mode">Switch to Dark Mode

<script>
const toggleDarkMode = document.querySelector('.js-toggle-dark-mode');

jtd.addEvent(toggleDarkMode, 'click', function(){
  if (jtd.getTheme() === 'dark') {
    jtd.setTheme('light');
    toggleDarkMode.textContent = 'Switch to Dark Mode';
  } else {
    jtd.setTheme('dark');
    toggleDarkMode.textContent = 'Switch to Light Mode';
  }
});
</script>

# Dashboard Data Types
{: .fs-9 }


## [1] asciiGraph

Runs a single Prometheus metric, and visualize the result on a live graph, where each metric result item represents a line on the graph

Using "`customKey`", allows you to control items names that show up colored right below the graph

> Example
```yaml
- name: Kafka Data In per second.
  box: right_a
  enable: true
  type: asciiGraph
  metricUnit: kb
  asciiGraphMetric: >
    sort_desc(sum(irate(kafka_server_brokertopicmetrics_bytesin_total{topic=~"$topic"}[5m])) by (strimzi_io_cluster, topic)) / 1024
  customKey: "🍅 {{topic}}"
  asciiGraphOptions:
    height: 0
    width: 80
    maxHeight: 17
    maxWidth: 45
    updateIntervalSeconds: 2
```


{: .warning }
> `asciiGraph` does NOT support "`autoConvertValue`" option

- "`metricUnit`" will added as it is beside the original metric value, Hence make sure that the metric returns the data in required unit to be visualized. ex: kb, mb, gb .. etc.


- [asciigraphoptions | Yaml Structure](./yaml_structure.md#asciigraphoptions)


<br>

---


## [2] progressBarList

Runs two Prometheus metrics "total value metric" & "usage value metric", Map them to get the usage percentage of each result items, and print a list of ProgressBars that show the usage & usage percentage of each result item

Using "`customKey`", allows you to control items names "Progress Bars Names"


> Example
```yaml
- name: Kafka pods memory usage (Sorted by higher memory usage)
  enable: true
  box: left_a
  type: progressBarList
  metricUnit: mb
  progressBarListMetrics:
    totalValueMetric: |
      # Memory limits
      sum(container_spec_memory_limit_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone)
    usageValueMetric: |
      # memory usage sorted by higher usage
      sort_desc(sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
  customKey: "{{pod}}"
  progressBarListOptions:
    maxItemsCount: 10
    lineBreak: true
    showBarPercentage: true
    barWidth: 25
    updateIntervalSeconds: 5
```

- [progressBarListMetrics | Yaml Structure](./yaml_structure.md#progressbarlistmetrics)
- [progressBarListOptions | Yaml Structure](./yaml_structure.md#progressbarlistoptions)


<br>

---


## [3] simpleTable

Runs a single Prometheus metric, and forms a table with all the result items as rows & all the sumed labels as columns

> Example
```yaml
- name: Kafka Pods memory usage (simpleTable example)
  enable: true
  box: left_b
  type: simpleTable
  metricUnit: byte
  simpleTableMetric: |
    sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, namespace, karpenter_sh_capacity_type, topology_kubernetes_io_zone,node_kubernetes_io_instance_type)
  customKey: "{{pod}}"
  simpleTableOptions:
    tableType: plain
    showValue: true
    headersUppercase: true
    autoConvertValue: true
    showTableIndex: true
    updateIntervalSeconds: 5
```


{: .highlight }
Table columns order is NOT garanteed with "simpleTable" Type


<br>

---


## [4] advancedTable

Runs a List of Prometheus metric, where each metric represents a Table column values

Using "`customKey`", allows you to control the values names of the "NAME" column


> Example
```yaml
- name: Kafka pods details (advancedTable example)
  enable: true
  box: left_c
  type: advancedTable
  advancedTableColumns:
    - memory usage:
      metric: |
        sort_desc(sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
      metricUnit: byte
      autoConvertValue: true
    - memory usage %:
      metric: |
        sort_desc(
          (
            sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone)
            /
            sum(container_spec_memory_limit_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone)
          ) * 100
        )
      metricUnit: percentage
      autoConvertValue: true
    - memory limit:
      metric: |
        sort_desc(sum(container_spec_memory_limit_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
      metricUnit: byte
      autoConvertValue: true
    - memory cache:
      metric: |
        sort_desc(sum(container_memory_cache{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
      metricUnit: byte
      autoConvertValue: true
    - memory swap:
      metric: |
        sum(container_memory_swap{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone)
      metricUnit: byte
      autoConvertValue: true
    - file descriptors:
      metric: |
        sort_desc(sum(container_file_descriptors{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
      metricUnit: None
    - up time:
      metric: |
        sum(time() - kube_pod_start_time{namespace=~"$namespace", pod=~"$pod"}) by (pod)
      metricUnit: seconds
      autoConvertValue: true
    - AWS AZ:
      metric: |
        sort_desc(sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod"}) by (pod, topology_ebs_csi_aws_com_zone))
      metricUnit: byte
      valueFromLabel: topology_ebs_csi_aws_com_zone
  customKey: "{{pod}}"
  advancedTableOptions:
    tableType: grid
    headersUppercase: true
    showTableIndex: true
    updateIntervalSeconds: 3
```

{: .new-title }
> Note
>
> The advancedTableColumns columns order define the Table columns order
