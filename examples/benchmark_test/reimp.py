# -*- coding: utf-8 -*-

import logging

from haven import GHaven as Haven, GBlueprint as Blueprint, GTimer as Timer
# from haven import THaven as Haven, TBlueprint as Blueprint, TTimer as Timer

from netkit.box import Box
# from kola_box import KolaBox as Box

from haven import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
