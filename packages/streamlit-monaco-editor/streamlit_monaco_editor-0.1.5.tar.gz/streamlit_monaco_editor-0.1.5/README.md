# 📝 Streamlit Monaco Editor &nbsp; [![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link]

Monaco Editor (Visual Studio Code) for Streamlit

```This is a fork of the original component (fork was made on 5.07.2025 from version 0.1.3).```

Changes in version 0.1.5:
- key support
- solution to the problem with clearing the editor value

## Demo

[![Open in Streamlit][share_badge]][share_link]

[![Preview][share_video]][share_link]

## Installation

```sh
pip install streamlit-monaco-editor
```

## Getting started

```python
from streamlit_monaco_editor import st_monaco
import streamlit as st

st.title("Streamlit Markdown Editor")

content = st_monaco(value="# Hello world", height="600px", language="markdown")

if st.button("Show editor's content"):
    st.write(content)
```

[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
[share_link]: https://vs-code.streamlit.app/
[share_video]: https://github.com/KayumovRu/streamlit-monaco-editor/raw/main/demo.gif
[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/KayumovRu/streamlit-monaco-editor
[pypi_badge]: https://badgen.net/pypi/v/streamlit-monaco-editor?icon=pypi&color=black&label
[pypi_link]: https://pypi.org/project/streamlit-monaco-editor
