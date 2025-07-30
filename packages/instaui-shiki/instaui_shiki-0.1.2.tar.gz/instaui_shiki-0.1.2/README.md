# instaui-shiki

<div align="center">

English| [简体中文](./README.md)

</div>

## 📖 Introduction
instaui-shiki is a Python library for syntax highlighting code snippets in the browser using [Shiki](https://github.com/shikijs/shiki).


## ⚙️ Installation

```bash
pip install instaui-shiki
```

## 🖥️ Usage
```python
from instaui import ui

@ui.page("/")
def test_page():
    ui.code("print('foo')")


ui.server().run()
```

