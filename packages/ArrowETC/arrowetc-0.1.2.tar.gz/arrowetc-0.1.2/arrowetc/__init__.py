from importlib.metadata import version, PackageNotFoundError

from .arrowetc import ArrowETC

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["ArrowETC"]