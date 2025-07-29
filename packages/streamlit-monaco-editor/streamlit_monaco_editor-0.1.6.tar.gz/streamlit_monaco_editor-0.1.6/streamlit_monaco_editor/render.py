from pathlib import Path
from streamlit.components.v1 import declare_component
from streamlit_monaco_editor.flags import RELEASE

render_component = declare_component(
    "streamlit_monaco_editor",
    path=(Path(__file__).parent / "frontend/build").resolve()
)
