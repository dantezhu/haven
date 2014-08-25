# -*- coding: utf-8 -*-

import logging

from haven import GHaven as App, GBlueprint as Blueprint
# from haven import THaven as App, TBlueprint as Blueprint
# from melon import Melon as App, Blueprint

from netkit.box import Box
# from kola_box import KolaBox as Box

from haven import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
