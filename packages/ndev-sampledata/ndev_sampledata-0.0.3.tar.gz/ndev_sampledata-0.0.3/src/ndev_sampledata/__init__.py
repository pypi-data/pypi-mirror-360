try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._sample_data import ndev_logo

__all__ = ("ndev_logo",)
