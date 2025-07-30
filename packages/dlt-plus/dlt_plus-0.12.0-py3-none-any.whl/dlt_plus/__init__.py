"""dlt+ is a plugin to OSS `dlt` adding projects, packages and new cli commands."""

from dlt_plus.version import __version__
from dlt_plus import current as _current

current = _current

__all__ = ["__version__", "current"]
