from setuptools import setup
from pathlib import Path
import os

# generate file for RELEASE flag
with open((Path(__file__).parent / "streamlit_monaco_editor/flags.py").resolve(), "w") as f:
    f.write(f"RELEASE = {os.environ.get('RELEASE') == 'true'}\n")

setup()
