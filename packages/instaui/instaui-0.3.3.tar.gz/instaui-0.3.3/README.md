# insta-ui

<div align="center">

English| [简体中文](./README.md)

</div>

## 📖 Introduction
insta-ui is a Python-based UI library for quickly building user interfaces.

## ⚙️ Features
Three modes:

- Web mode: Generate web (stateless) applications.
- Web View mode: Generate web view applications that can be packaged as native apps (no need to start a web server).
- Zero mode: Generate pure HTML files that run directly in browsers without any dependencies.

 
## 📦 Installation

Zero mode:

```
pip install instaui -U
```

web mode

```
pip install instaui[web] -U
```

Web View mode
```
pip install instaui[webview] -U
```


## 🖥️ Quick Start
Below is a simple example of number summation. The result color changes dynamically based on the sum:

```python
from instaui import ui, arco
arco.use()

@ui.page('/')
def home():
    num1 = ui.state(0)
    num2 = ui.state(0)

    # Automatically recalculates result when num1 or num2 changes 
    @ui.computed(inputs=[num1, num2])
    def result(num1: int, num2: int):
        return num1 + num2

    # Automatically updates text_color when result changes
    @ui.computed(inputs=[result])
    def text_color(result: int):
        return "red" if result % 2 == 0 else "blue"

    # UI components  
    arco.input_number(num1)
    ui.label("+")
    arco.input_number(num2)
    ui.label("=")
    ui.label(result).style({"color": text_color})

# when you deploy your web application, you need to set debug=False.
ui.server(debug=True).run()
```

Replace `ui.server().run()` with `ui.webview().run()` to switch to Web View mode:

```python
...

# ui.server(debug=True).run()
ui.webview().run()
```

To execute computations on the client side instead of the server, use `ui.js_computed` instead of `ui.computed`:

```python
from instaui import ui, arco
arco.use()

@ui.page('/')
def home():
    num1 = ui.state(0)
    num2 = ui.state(0)

    result = ui.js_computed(inputs=[num1, num2], code="(num1, num2) => num1 + num2")
    text_color = ui.js_computed(inputs=[result], code="(result) => result % 2 === 0? 'red' : 'blue'")

    # UI components
    ...

...

```

In this case, all interactions will run on the client side. Use `Zero mode` to generate a standalone HTML file:

```python
from instaui import ui, arco,zero
arco.use()

@ui.page('/')
def home():
    num1 = ui.state(0)
    num2 = ui.state(0)

    result = ui.js_computed(inputs=[num1, num2], code="(num1, num2) => num1 + num2")
    text_color = ui.js_computed(inputs=[result], code="(result) => result % 2 === 0? 'red' : 'blue'")

    # UI components
    arco.input_number(num1)
    ui.label("+")
    arco.input_number(num2)
    ui.label("=")
    ui.label(result).style({"color": text_color})

with zero() as z:
    home()
    z.to_html('index.html')

```