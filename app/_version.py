# std
from pathlib import Path

# vendor
import toml

# local

with open(Path(__file__).parent.parent / "pyproject.toml") as pyproject_toml:
    pyproject = toml.load(pyproject_toml)

print(pyproject)
__version__ = pyproject["tool"]["poetry"]["version"]
