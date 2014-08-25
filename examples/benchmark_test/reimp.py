# -*- coding: utf-8 -*-

import logging

from haven import GHaven as Haven, GBlueprint as Blueprint
# from haven import THaven as Haven, TBlueprint as Blueprint
# from melon import Melon, Blueprint

from netkit.box import Box
# from kola_box import KolaBox as Box

from haven import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
