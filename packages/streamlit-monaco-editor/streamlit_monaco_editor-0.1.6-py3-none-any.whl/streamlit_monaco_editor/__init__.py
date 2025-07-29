from streamlit_monaco_editor.render import render_component

__version__ = "0.1.6"


def st_monaco(
    value="",
    height="200px",
    language="markdown",
    lineNumbers=True,
    minimap=False,
    theme="streamlit",
    key=None,
):
    return render_component(
        value=value,
        height=height,
        language=language,
        lineNumbers=lineNumbers,
        minimap=minimap,
        theme=theme,
        key=key,
    )
