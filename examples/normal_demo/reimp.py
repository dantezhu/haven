# -*- coding: utf-8 -*-

import logging

from haven import GHaven as Haven, GBlueprint as Blueprint, GTimer as Timer
# from haven import THaven as Haven, TBlueprint as Blueprint, TTimer as Timer

from netkit.box import Box

from haven import logger

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
