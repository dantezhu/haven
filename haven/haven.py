# -*- coding: utf-8 -*-

from .callbacks_mixin import AppCallBacksMixin


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
