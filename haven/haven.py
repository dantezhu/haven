# -*- coding: utf-8 -*-

from .callbacks_mixin import AppCallBacksMixin
from . import autoreload


class Haven(AppCallBacksMixin):
    debug = False
    use_reloader = None
    got_first_request = False
    blueprints = None

    def __init__(self):
        super(Haven, self).__init__()
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)

    def run(self, host, port, debug=None, use_reloader=None):
        if debug is not None:
            self.debug = debug

        self.use_reloader = use_reloader if use_reloader is not None else self.debug

        if self.use_reloader:
            autoreload.main(self._run, (host, port))
        else:
            self._run(host, port)

    def _run(self, host, port):
        raise NotImplementedError
