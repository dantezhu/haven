# -*- coding: utf-8 -*-

from multiprocessing import Process
from .callbacks_mixin import AppCallBacksMixin
from . import autoreload
from .log import logger


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
    blueprints = None

    def __init__(self):
        super(Haven, self).__init__()
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)

    def run(self, host, port, debug=None, use_reloader=None, workers=None):
        if debug is not None:
            self.debug = debug

        use_reloader = use_reloader if use_reloader is not None else self.debug

        def run_wrapper():
            logger.info('Running server on %s:%s, debug: %s, use_reloader: %s',
                        host, port, self.debug, use_reloader)
            self._start_repeat_timers()

            self._prepare_server(host, port)
            if workers is not None:
                proc_list = []
                for it in xrange(0, workers):
                    p = Process(target=self._serve_forever)
                    # 当前进程_daemonic默认是False，改成True将启动不了子进程
                    # 但是子进程要设置_daemonic为True，这样父进程退出，子进程会被强制关闭
                    p._daemonic = True
                    p.start()
                    proc_list.append(p)

                for it in proc_list:
                    try:
                        it.join()
                    except KeyboardInterrupt:
                        pass
            else:
                try:
                    self._serve_forever()
                except KeyboardInterrupt:
                    pass

        if use_reloader:
            autoreload.main(run_wrapper)
        else:
            run_wrapper()

    def repeat_timer(self, interval):
        raise NotImplementedError

    def _prepare_server(self, host, port):
        raise NotImplementedError

    def _serve_forever(self):
        raise NotImplementedError

    def _start_repeat_timers(self):
        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()