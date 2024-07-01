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
