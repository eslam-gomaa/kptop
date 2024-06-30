---
layout: default
nav_order: 2
# permalink: /
# parent: Home
permalink: /commands
title: Custom Commands Docs
markdown: Kramdown
has_children: true
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

# Custom Commands
{: .fs-9 }

Create monitoring dasboards on the terminal easily with a simple yaml file !

<br>

## Examples
- [pods.yml](../../examples/dashboards/pods.yml)
- [pvcs.yml](../../examples/dashboards/pvcs.yml)

<br>

---

<br>

## List commands

```bash
kptop --list-commands
```


## Run command


```bash
kptop --command <DASHBOARD-NAME>
```

<br>

---

## Command YAMl structure

To be added.