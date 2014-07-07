# -*- coding: utf-8 -*-

__version__ = '1.0.25'

from .log import logger
from .blueprint import Blueprint

try:
    from gevent_impl import GHaven, GLater
except:
    GeventHaven = None

from thread_impl import THaven, TLater
