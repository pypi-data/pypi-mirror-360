"""
functionwordsets – API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exposes:
    • FunctionWordSet  – frozen dataclass with the set
    • load(id_)        – load one dataset (defaults to "fr_21c")
    • available_ids()  – list all dataset IDs found in ./datasets
"""

from importlib.metadata import version, PackageNotFoundError
from ._loader import FunctionWordSet, load, available_ids

try:
    __version__ = version("functionwordsets")
except PackageNotFoundError:          # editable / dev install
    __version__ = "0.0.0"

__all__ = [
    "FunctionWordSet",
    "load",
    "available_ids",
    "__version__",
]
