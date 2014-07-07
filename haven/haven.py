# -*- coding: utf-8 -*-

from .callbacks_mixin import AppCallBacksMixin


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
    blueprints = None

    def __init__(self):
        super(Haven, self).__init__()
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)
