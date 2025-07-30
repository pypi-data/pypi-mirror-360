# Lilliepy-Tags

A JSX-like transpiler for [ReactPy](https://reactpy.dev/) projects written in Python. This tool allows you to write familiar JSX-style syntax inside Python component return blocks, and transpile them into proper ReactPy functional calls.

---

## 📦 Features

- ✅ Supports nested tags
- ✅ Supports `{expression}` embedding inside text or tags
- ✅ Processes multiple `@component` functions per file
- ✅ Supports multiple return blocks (in if/else/loop branches)
- ✅ Converts `.x.py` files in a folder into clean Python ReactPy code
- ✅ Outputs to a `dist/` folder under a custom name

---

## 📂 Example Input (test.x.py)

```python
from reactpy import component, run, html

var = "Hello, world!"

@component
def App():
    return (
        <html.h1 id="greeting" class="main">
            {var}
        </html.h1>
    )

run(App)
```

---

## 📦 Output (in dist/build/test.x.py)

```python
from reactpy import component, run, html

var = "Hello, world!"

@component
def App():
    return (
        html.h1(
            {
                "id": "greeting",
                "class": "main",
            },
            var
        )
    )

run(App)
```

---

## 📖 Usage

### 📦 Install dependencies (if any)
Currently no external pip dependencies needed.

### 🏃 Run the transpiler

```python
from lilliepy_tags import Lilliepy_Tags

process_folder("src", "dist/build")
```

- `src` is the folder containing your `.x.py` files.
- `dist/build` is your chosen output directory.