---
layout: default
nav_order: 2
# permalink: /
parent: Custom Commands
title: Command Data Types
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

<br>


## [1] advancedTable

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

- [advancedTableColumns > Yaml Structure](./yaml_structure.md#advancedtablecolumns)
- [advancedTableOptions > Yaml Structure](./yaml_structure.md#advancedtableoptions)
