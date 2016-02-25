# -*- coding: utf-8 -*-

from collections import Counter

from .mixins import RoutesMixin, AppEventsMixin
from . import autoreload
from .log import logger
from . import constants


class Haven(RoutesMixin, AppEventsMixin):
    debug = False
    got_first_request = False
    blueprints = None

    def __init__(self):
        RoutesMixin.__init__(self)
        AppEventsMixin.__init__(self)
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register_to_app(self)

    def run(self, host=None, port=None, debug=None, use_reloader=None):
        self._validate_cmds()

        if host is None:
            host = constants.SERVER_HOST
        if port is None:
            port = constants.SERVER_PORT
        if debug is not None:
            self.debug = debug

        use_reloader = use_reloader if use_reloader is not None else self.debug

        def run_wrapper():
            logger.info('Running server on %s:%s, debug: %s, use_reloader: %s',
                        host, port, self.debug, use_reloader)

            self._prepare_server(host, port)
            self._try_serve_forever()

        if use_reloader:
            autoreload.main(run_wrapper)
        else:
            run_wrapper()

    def acquire_got_first_request(self):
        pass

    def release_got_first_request(self):
        pass

    def repeat_timer(self, interval):
        raise NotImplementedError

    def _validate_cmds(self):
        """
        确保 cmd 没有重复
        :return:
        """

        cmd_list = list(self.rule_map.keys())

        for bp in self.blueprints:
            cmd_list.extend(bp.rule_map.keys())

        duplicate_cmds = (Counter(cmd_list) - Counter(set(cmd_list))).keys()

        assert not duplicate_cmds, 'duplicate cmds: %s' % duplicate_cmds

    def _before_worker_run(self):
        self.events.create_worker()
        for bp in self.blueprints:
            bp.events.create_app_worker()

        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()

    def _try_serve_forever(self):
        self._before_worker_run()

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)

    def _prepare_server(self, host, port):
        raise NotImplementedError

    def _serve_forever(self):
        raise NotImplementedError
