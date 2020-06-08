__version__ = '1.2.3'

from .log import logger
from .utils import safe_call, safe_func

try:
    from .gevent_impl import GHaven, GBlueprint, GTimer
except:
    GHaven = GBlueprint = GTimer = None

from .thread_impl import THaven, TBlueprint, TTimer
