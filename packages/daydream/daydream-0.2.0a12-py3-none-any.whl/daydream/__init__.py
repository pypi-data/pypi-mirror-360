from importlib.metadata import version as get_version
from typing import cast

from .sentry import *  # noqa: F403
from .warnings import *  # noqa: F403

__version__ = get_version(cast("str", __package__))
