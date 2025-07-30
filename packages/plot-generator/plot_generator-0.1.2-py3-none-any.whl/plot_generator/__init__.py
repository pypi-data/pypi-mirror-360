from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("plot-generator")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.1"

from .server import mcp       