from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pyralgen")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .generator import generate_ral

__all__ = [
    "__version__",
    "generate_ral",
]