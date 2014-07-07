# -*- coding: utf-8 -*-

__version__ = '1.0.19'

from .log import logger
from .blueprint import Blueprint

try:
    from gevent_impl import GeventHaven
except:
    GeventHaven = None

from thread_impl import ThreadHaven
