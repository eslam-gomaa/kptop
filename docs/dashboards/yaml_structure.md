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

Create monitoring dasboards on the terminal easily with a simple yaml file !

<br>


## dashboard

Required
{: .label .label-yellow }

Dict
{: .label .label-purple }

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
{: .label .label-green }


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
{: .label .label-green }

|            | type | description                             | default | required |
| ------------ | ------ | ----------------------------------------- | --------- | ---------- |
| enable     | `Boolean`<br />   | Whether to enable the screen split mode | False   | False    |
| size<br />     | `Integer`     | Layout Size                             | True    | False    |
| ratio<br />    | `Dict`     | Layout Ratio                            | <br />      | False    |
| split_mode | `Dict`     | Split option, Options: `column` , `row`              | "row"   | False    |
| split      | `Dict`     | Furthur split                           |         | True     |
