# -*- coding: utf-8 -*-

from .base import AppCallBacksMixin


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
