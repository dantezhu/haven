# -*- coding: utf-8 -*-

import logging

from netkit.box import Box

from haven import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
