from .base import *  # NOQA: F401, F403

DEBUG = False

try:
    from .local import *  # NOQA: F401, F403
except ImportError:
    pass
