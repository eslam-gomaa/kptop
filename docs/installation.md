---
layout: default
nav_order: 1
# permalink: /
# parent: Home
permalink: /installation
title: Installation
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

# Install KPtop
{: .fs-9 }


> Compatible with Python 3.6+

[on PyPi](https://pypi.org/project/kptop)

```bash
pip3 install kptop --upgrade
```
