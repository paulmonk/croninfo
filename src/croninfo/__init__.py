from __future__ import annotations

import sys

from croninfo.crontab import Crontab

# Import metadata (using importlib_metadata backport for python versions <3.8)
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__all__ = ("Crontab",)

__version__ = metadata.version("croninfo")

# Check major python version
if sys.version_info[0] < 3:
    raise Exception("Croninfo does not support Python 2. Please upgrade to Python 3.")
# Check minor python version
elif sys.version_info[1] < 7:
    raise Exception(
        "Croninfo %s only supports Python 3.7+. "
        "Use a later version of Python for support." % __version__
    )
