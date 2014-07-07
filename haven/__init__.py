# -*- coding: utf-8 -*-

__version__ = '1.0.28'

from .log import logger
from .blueprint import Blueprint

try:
    from gevent_impl import GHaven, GLater
except:
    GHaven = GLater = None

from thread_impl import THaven, TLater
