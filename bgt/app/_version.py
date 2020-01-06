# std
from pathlib import Path

# vendor
import toml

# local

with open(Path(__file__).parent.parent.parent / "pyproject.toml") as pyproject_toml:
    pyproject = toml.load(pyproject_toml)

__version__ = pyproject["tool"]["poetry"]["version"]
