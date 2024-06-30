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
