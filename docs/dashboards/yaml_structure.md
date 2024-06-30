---
layout: default
nav_order: 1
# permalink: /
parent: Custom Dashboards
title: Dashboard YAML structure
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

# Dashboard YAML structure
{: .fs-9 }

Create monitoring dasboards on the terminal easily with simple yaml files !

<br>


## dashboard

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }

|               | type | description                                           | default | required |
| --------------- | ------ | ------------------------------------------------------- | --------- | ---------- |
| name          | `String`<br />   | Dashboard name                                        |         | True     |
| description<br /> | `String`     | Dashboard description                                 |         | False    |
| layout<br />      | `Dict`     | The dashbaord layout structure                        | <br />      | True     |
| variables     | `List`     | CLI argument options for the variable                 |         | False    |
| visualization | `List`     | List of graphs to display on the defined layout boxes |         | True     |

---

## layout

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }


|              | type | description                         | default | required |
| -------------- | ------ | ------------------------------------- | --------- | ---------- |
| splitMode    | `String`<br />   | Split                               | "row"   | False    |
| fullScreen<br /> | `Boolean`     | Dashboard description               | True    | False    |
| header<br />     | `Dict`     | Dashboard header options            | <br />      | False    |
| body.boxes   | `Dict`     | Options of the 3 main screen splits |         | True     |


### left || middle || right

Optional
{: .label .label-green }

Dict
{: .label .label-blue }


> **Example**
```yaml
left:
  enable: true
  size: 190
  ratio: 1
  split_mode: column
  split:
    left_a:
      size: 0
      ratio: 1
```


|            | type | description                             | default | required |
| ------------ | ------ | ----------------------------------------- | --------- | ---------- |
| enable     | `Boolean`<br />   | Whether to enable the screen split mode | False   | False    |
| size<br />     | `Integer`     | Layout Size                             | 0       | False    |
| ratio<br />    | `Integer`     | Layout Ratio                            | 1       | False    |
| split_mode | `Dict`     | Split option, Options: `column` , `row`              | "row"   | False    |
| split      | `Dict`     | Furthur split                           |         | True     |


#### [left || middle || right].split

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|            | type | description  | default | required |
| ------------ | ------ | -------------- | --------- | ---------- |
| SPLIT-NAME | `Dict`<br />   | **User Input - ​**             | False   | False    |
| size<br />     | `Integer`     | Layout Size  | 0       | False    |
| ratio<br />    | `Integer`     | Layout Ratio | 1       | False    |

---

## Variables

Optional
{: .label .label-green }

List
{: .label .label-blue }


> **Example**
```yaml
variables:
  - name: namespace
    default: .*
    cliArgument:
      enable: true
      short: -n
      required: false
  - name: pod
    default: .*
    cliArgument:
      enable: true
      short: -po
      required: false
```

|               | type | description                                          | default | required |
| --------------- | ------ | ------------------------------------------------------ | --------- | ---------- |
| name          | `String`     | variable name ,, also used for the CLI argument name |         | True     |
| default<br />     | `String`     | devault value for the variable                       |         | True     |
| cliArgument<br /> | `Dict`     | CLI argument options for the variable                | <br />      | False    |


### cliArgument

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|            | type | description                                        | default | required |
| ------------ | ------ | ---------------------------------------------------- | --------- | ---------- |
| enable     | `Boolean`     | Enable CLI argument for the variable               |         | True     |
| short<br />    | `String`     | short for the argument                             |         | True     |
| required<br /> | `Boolean`     | Wether the argument is required to run the command | False   | False    |

---

## Visualization

Required
{: .label .label-yellow }

List
{: .label .label-blue }


> **Example**
```yaml
visualization:
  - name: Pods Memory Usage
    enable: true
    box: right_a
    type: asciiGraph
    metricUnit: mb
    # Sorting is important if you expect lots of results
    asciiGraphMetric: >
      sort_desc(sum(container_memory_usage_bytes{namespace=~"$namespace", pod=~"$pod", pod!=""}) by (pod) / 1024 / 1024)
    custom_key: "🥕 {{pod}}"
    asciiGraphOptions:
      height: 0
      width: 80
      maxHeight: 17
      maxWidth: 45
      updateIntervalSeconds: 2
```

|                        | type | description                                                                                                                            | default                   | required |
| ------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------- |
| name                   | `String`     | Name of graph                                                                                                                          |                           | True     |
| enable<br />               | `Boolean`     | Enable the display of the graph                                                                                                        | True                      | False    |
| box<br />                  | `Boolean`     | The layout box to display the graph in,<br />*Example*: `right` , `right_a` , `left_b`                                                                                      | <br />                        | True     |
| type                   |      | Graph data type - Options: [`asciiGraph`, `progressBarList`, `simpleTable`, `advancedTable`]                                                                                                    |                           | True     |
| metricUnit             | `String`     | the metirc value unit - Options: [`None`, `byte`, `mb`, `gb`, `tb`, `seconds`, `percentage`]                                                                                        |                           |          |
| custom_key             | `String`     | custom key for the metric result key, <br />*Example: ​*​`🥕 {{pod}}`  would be translated to `🥕 POD-NAME` <br />                                                                   | Metric default result key |          |
| asciiGraphOptions      | `Dict`     | Graph options with `asciiGraph` data type                                                                                                          |                           | False    |
| progressBarListOptions | `Dict`     | Graph options with `progressBarList` data type                                                                                                          |                           | False    |
| simpleTableOptions     | `Dict`     | Graph options with `simpleTable` data type                                                                                                          |                           | False    |
| advancedTableOptions   | `Dict`     | Graph options with `advancedTable` data type                                                                                                          |                           | False    |
| simpleTableMetric      | `String`     | **Required with ​`simpleTable`​ Data type**<br />A single Prometheus Metric, where each result item is a row in the table and each label is a column.                                 |                           | True     |
| advancedTableColumns   | `Dict`     | **Required with ​​`advancedTable`​ Data type**<br />List of metrics, where each metric represent a column on the table                                                                   |                           | True     |
| progressBarListMetrics | `Dict`     | **Required with ​`progressBarList`​ Data type**<br />Two Prometheus metrics, "usage" & "total" , to calculate and display the percentage of each result item and display as a progressBar |                           | True     |
| asciiGraphMetric       | `String`     | **Required with ​`asciiGraph`​ Data type**<br />A single Prometheus Metric, where each result item is a line on the graph                                                            |                           | True     |

<br>

### asciiGraphOptions

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|                       | type | description          | default | required |
| ----------------------- | ------ | ---------------------- | --------- | ---------- |
| height                | `Integer`     | Graph height         | 17<br />    | False    |
| width<br />               | `Integer`     | Graph width          | 45      | False    |
| maxHeight             | `Integer`     |                      | 20      | False    |
| maxWidth<br />            | `Integer`     | <br />                   | 50      | False    |
| updateIntervalSeconds | `Integer`     | Data update interval | 5       | False    |

### progressBarListOptions

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|                       | type | description                               | default | required |
| ----------------------- | ------ | ------------------------------------------- | --------- | ---------- |
| maxItemsCount         | `Integer`     | Maxumim number of items to visualize      | 20      | False    |
| lineBreak<br />           | `Boolean`     | Print lines between progressBars          | True    | False    |
| showBarPercentage     | `Boolean`     | show progress percentage for ProgressBars | True<br />  | False    |
| barWidth<br />            | `Integer`     | ProgressBar width                         | 20<br />    | False    |
| updateIntervalSeconds | `Integer`     | Data update interval                      | 5       | False    |


### simpleTableOptions

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|                       | type | description                                                                                                                                   | default | required |
| ----------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| tableType             | `String`     | Table type  - [Allowed Options](https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format)                                                                                                                                | plain   | False    |
| showValue<br />           | `Boolean`     | Show value column                                                                                                                             | True    | False    |
| headersUppercase      | `Boolean`     | Show the table header in Upecase                                                                                                              | True<br />  | False    |
| autoConvertValue<br />    | `Boolean`     | Auto convert the metric value based on the metricUnit .. for example, if metric value is in byte, it would be converted to kb, mb, gb .. etc. | False   | False    |
| showTableIndex        | `Boolean`     | Show table Index on the left                                                                                                                  | True<br />  | False    |
| updateIntervalSeconds | `Integer`     | Data update interval                                                                                                                          | 5       | False    |


### advancedTableOptions

Optional
{: .label .label-green }

Dict
{: .label .label-blue }

|                       | type | description                                                                                                                                   | default | required |
| ----------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| tableType             | `String`     | Table type  - [Allowed Options](https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format)                                                                                                                                | plain   | False    |
| showValue<br />           | `Boolean`     | Show value column                                                                                                                             | True    | False    |
| headersUppercase      | `Boolean`     | Show the table header in Upecase                                                                                                              | True<br />  | False    |
| autoConvertValue<br />    | `Boolean`     | Auto convert the metric value based on the metricUnit .. for example, if metric value is in byte, it would be converted to kb, mb, gb .. etc. | False<br /> | False    |
| showTableIndex        | `Boolean`     | Show table Index on the left                                                                                                                  | True<br />  | False    |
| updateIntervalSeconds | `Integer`     | Data update interval                                                                                                                          | 5       | False    |

<br>


### advancedTableColumns

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }

|                      | type | description                                                                                                                                   | default | required |
| ---------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| COULMN NAME <br />EX: `- memory usage:`<br /> | `String`     | Column name (User Input name)                                                                                                                 | plain   | True     |
| metric<br />             | `String`     | Prometheus metric to qurey                                                                                                                    | <br />      | True     |
| metricUnit           | `String`     | metric result value unit<br />Options: [`None`, `kb`, `byte`, `mb`, `gb`, `tb`, `seconds`, `percentage`]                                                                                           | byte    | False    |
| autoConvertValue<br />   | `Boolean`     | Auto convert the metric value based on the metricUnit .. for example, if metric value is in byte, it would be converted to kb, mb, gb .. etc. | False   | False    |


### progressBarListMetrics

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }

|                      | type | description                                      | default | required |
| ---------------------- | ------ | -------------------------------------------------- | --------- | ---------- |
| total_value_metric   | `String`     | Prometheus metric to qurey - to get total values |         | True     |
| total_value_metric<br /> | `String`     | Prometheus metric to qurey - to get usage values | <br />      | True     |
