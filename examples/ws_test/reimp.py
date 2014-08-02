# -*- coding: utf-8 -*-

import logging

#from netkit.box import Box as Box
from kola_box import KolaBox as Box

from haven import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
