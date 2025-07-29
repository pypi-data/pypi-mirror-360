from importlib.metadata import version, PackageNotFoundError
from ._loader import FunctionWordSet, load, available_ids

try:
    __version__ = version("functionwords")
except PackageNotFoundError:   # dev checkout
    __version__ = "0.0.0"

__all__ = ["FunctionWordSet", "load", "available_ids", "__version__"]
