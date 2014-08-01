# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('main')

#from netkit.box import Box as Box
from kola_box import KolaBox as Box

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
