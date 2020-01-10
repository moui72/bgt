# Standard lib
from pathlib import Path

# Vendor
import toml

with open(Path(__file__).parent.parent / "pyproject.toml") as pyproject_toml:
    pyproject = toml.load(pyproject_toml)

__version__ = pyproject["tool"]["poetry"]["version"]
