# -*- coding: utf-8 -*-

import logging

from haven import GHaven as App, GBlueprint as Blueprint
# from haven import THaven as App, TBlueprint as Blueprint
# from melon import Melon as App, Blueprint

from netkit.box import Box
# from kola_box import KolaBox as Box

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
