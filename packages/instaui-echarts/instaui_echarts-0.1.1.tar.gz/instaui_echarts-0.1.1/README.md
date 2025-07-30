# instaui-echarts

<div align="center">

English| [简体中文](./README.md)

</div>

## 📖 Introduction
instaui-echarts is a Python package for instaui, which provides a component for rendering ECharts.


## ⚙️ Installation

```bash
pip install instaui-echarts
```

## 🖥️ Usage
```python
from instaui import ui

@ui.page("/")
def test_page():
    opts = {
        "title": {"text": "ECharts Getting Started Example"},
        "tooltip": {},
        "legend": {"data": ["sales"]},
        "xAxis": {
            "data": ["Shirts", "Cardigans", "Chiffons", "Pants", "Heels", "Socks"]
        },
        "yAxis": {},
        "series": [{"name": "sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
    }

    ui.echarts(opts)


ui.server().run()
```

