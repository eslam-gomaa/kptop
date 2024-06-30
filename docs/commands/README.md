
# KPtop Custom Commands

You can create monitoring command lines easily with a simple yaml file !



## Examples
- [pods.yml](../examples/commands/pods.yml)
- [pods-wide.yml](../examples/commands/pods-wide.yml)
- [pvcs.yml](../examples/commands/pvcs.yml)


## Command YAMl structure


### variables

Take a list of variables, and optionally you can set a CLi argument for a variable

|               | type | description                                          | default | required |
| --------------- | ------ | ------------------------------------------------------ | --------- | ---------- |
| name          | `String`     | variable name ,, also used for the CLI argument name |         | True     |
| default<br />     | `String`     | devault value for the variable                       |         | <br />       |
| cliArgument<br /> | `Dict`     | CLI argument options for the variable                | <br />      |          |


### cliArgument

|            | type | description                                        | default | required |
| ------------ | ------ | ---------------------------------------------------- | --------- | ---------- |
| enable     | `Boolean`     | Enable CLI argument for the variable               |         | True     |
| short<br />    | `String`     | short for the argument                             |         | True     |
| required<br /> | `Boolean`     | Wether the argument is required to run the command | False   | False    |


### execute (dict)

|                      | type | description                                                                      | default                                                         | required | options |
| ---------------------- | ------ | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------- | --------- |
| type                 | `String`     | Data type to display on the terminal                                             |                                                                 | True     | `advancedTable`        |
| advancedTableColumns | `List`     | List of coulmns for the table, each column has its own metric                    |                                                                 | True     |         |
| custom_key           | `String`     | specify a custom key for metric result, You can compensate labels with "`{{LABEL}}`" syntax | default labels result (string composed of summed labels .. ex. `sum(metric) by (pod, namespace)` |          |         |
| advancedTableOptions | `Dict`     | options to control how the resulted table looks                                  |                                                                 |          |         |


### advancedTableColumns

|                      | type | description                                                                                                                                   | default | required | options        |
| ---------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- | ---------------- |
| COULMN NAME <br />EX: `- memory usage:`<br /> | `String`     | <br />                                                                                                                                            |         | <br />       | <br />             |
| metric               | `String`<br />   | Prometheus metric to qurey                                                                                                                    |         | <br />       |                |
| metricUnit<br />         | `String`<br />   | metric result value unit                                                                                                                      | byte    |          | `None`, `kb`, `byte`, `mb`, `gb`, `tb`, `seconds`, `percentage` |
| autoConvertValue<br />   | `Boolean`<br />   | Auto convert the metric value based on the metricUnit .. for example, if metric value is in byte, it would be converted to kb, mb, gb .. etc. | False   | False    |                |


### advancedTableOptions

|                    | type | description                                    | default | required | options |
| -------------------- | ------ | ------------------------------------------------ | --------- | ---------- | --------- |
| tableType          | `String`     | the type of table, defines how the table looks | plain   | False    | [All the types supported here](https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format) 🙂<br />   |
| headersUppercase<br /> | `Boolean`     | <br />                                             | True    | False    |         |
| showTableIndex<br />   | `Boolean`<br />   | how table idex on the left                     | False   | False    |         |


<br>

---

<br>


## List commands

```bash
kptop --list-commands
```


## Run command


```bash
kptop --command <COMMAND-NAME>
```
