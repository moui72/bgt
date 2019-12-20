import toml
from pathlib import Path

with open(Path(__file__).parent.parent / "pyproject.toml") as pyproject_toml:
    pyproject = toml.load(pyproject_toml)

print(pyproject)
__version__ = pyproject["tool"]["poetry"]["version"]
