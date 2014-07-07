# -*- coding: utf-8 -*-

__version__ = '1.0.19'

from .log import logger
from .blueprint import Blueprint

try:
    from gevent_haven import GeventHaven
except:
    GeventHaven = None

from thread_haven import ThreadHaven
