"""TrackDo package.

TrackDo is a Todo Manager made in Python with lower level primitives made to be used through other interfaces.
"""

from __future__ import annotations

from importlib.metadata import version

try:
    __version__ = version("trackdo")
except Exception:
    __version__ = "unknown"

from trackdo._internal.cli import main

__all__: list[str] = ["__version__", "main"]
