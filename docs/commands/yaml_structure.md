---
layout: default
nav_order: 1
# permalink: /
parent: Custom Commands
title: Command YAML structure
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



[**Full commands Examples Directory**](https://github.com/eslam-gomaa/kptop/blob/v0.0.10/examples/commands)


<br>


## command

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }

|               | type | description                                   | default | required |
| --------------- | ------ | ----------------------------------------------- | --------- | ---------- |
| name          | `String`<br />   | Command name                                  |         | True     |
| description<br /> | `String`     | Command description                           |         | False    |
| variables     | `List`     | List of variables with optional CLI arguments |         | False    |
| execute       | `Dict`     | Data type to execute                          |         | True     |

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

## execute

Required
{: .label .label-yellow }

Dict
{: .label .label-blue }

|                             | type | description                                                          | default                                                         | required |
| ----------------------------- | ------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------- |
| type<br />                      | `String`<br />   | Data type<br />Options: [`advancedTable`]                                               |                                                                 | True     |
| advancedTableColumns<br />      | `List`     | **Required with ​**​`advancedTable`​**​ Data type**<br />List of metrics, where each metric represent a column on the table |                                                                 | True     |
| custom_key                  | `String`     | custom key for the metric result key, <br />*Example: ​*​`🥕 {{{{pod}}}}`  would be translated to `🥕 POD-NAME` <br /> | default labels result (string composed of summed labels .. ex. `sum(metric) by (pod, namespace)` | False    |
| executeadvancedTableOptions | `Dict`     | Graph options with `advancedTable` data type                                        |                                                                 | False    |


<br>


### advancedTableColumns

Required
{: .label .label-yellow }

List
{: .label .label-blue }

|                      | type | description                                                                                                                                   | default | required |
| ---------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| COULMN NAME <br />EX: `- memory usage:`<br /> | `String`     | Column name (User Input name)                                                                                                                 | plain   | True     |
| metric<br />             | `String`     | Prometheus metric to qurey                                                                                                                    | <br />      | True     |
| metricUnit           | `String`     | metric result value unit<br />Options: [`None`, `kb`, `byte`, `mb`, `gb`, `tb`, `seconds`, `percentage`]                                                                                           | byte    | False    |
| autoConvertValue<br />   | `Boolean`     | Auto convert the metric value based on the metricUnit .. for example, if metric value is in byte, it would be converted to kb, mb, gb .. etc. | False   | False    |

<br>


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