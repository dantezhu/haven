# -*- coding: utf-8 -*-

from multiprocessing import Process
import time
import signal
from .callbacks_mixin import AppCallBacksMixin
from . import autoreload
from .log import logger
from . import constants


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
    blueprints = None

    def __init__(self):
        super(Haven, self).__init__()
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)

    def run(self, host=None, port=None, debug=None, use_reloader=None, workers=None, handle_signals=None):
        if host is None:
            host = constants.SERVER_HOST
        if port is None:
            port = constants.SERVER_PORT
        if debug is not None:
            self.debug = debug

        use_reloader = use_reloader if use_reloader is not None else self.debug
        handle_signals = handle_signals if handle_signals is not None else not use_reloader

        def run_wrapper():
            logger.info('Running server on %s:%s, debug: %s, use_reloader: %s',
                        host, port, self.debug, use_reloader)

            self._before_run()

            self._prepare_server(host, port)
            if workers is not None:
                if handle_signals:
                    # 因为只能在主线程里面设置signals
                    self._handle_parent_proc_signals()

                self._fork_workers(workers)
            else:
                self._try_serve_forever(True)

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

    def _before_run(self):
        self._start_repeat_timers()

    def _try_serve_forever(self, main_process):
        if not main_process:
            self._handle_child_proc_signals()

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)

    def _fork_workers(self, workers):
        def start_worker_process():
            inner_p = Process(target=self._try_serve_forever, args=(False,))
            # 当前进程daemon默认是False，改成True将启动不了子进程
            # 但是子进程要设置daemon为True，这样父进程退出，子进程会被强制关闭
            inner_p.daemon = True
            inner_p.start()
            return inner_p

        p_list = []

        for it in xrange(0, workers):
            p = start_worker_process()
            p_list.append(p)

        while 1:
            for idx, p in enumerate(p_list):
                if not p.is_alive():
                    old_pid = p.pid
                    p = start_worker_process()
                    p_list[idx] = p

                    logger.error('process[%s] is dead. start new process[%s].', old_pid, p.pid)

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except:
                logger.error('exc occur.', exc_info=True)
                break

    def _handle_parent_proc_signals(self):
        # 修改SIGTERM，否则父进程被term，子进程不会自动退出；明明子进程都设置为daemon了的
        signal.signal(signal.SIGTERM, signal.default_int_handler)
        # 即使对于SIGINT，SIG_DFL和default_int_handler也是不一样的，要是想要抛出KeyboardInterrupt，应该用default_int_handler
        signal.signal(signal.SIGINT, signal.default_int_handler)

    def _handle_child_proc_signals(self):
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _start_repeat_timers(self):
        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()

    def _prepare_server(self, host, port):
        raise NotImplementedError

    def _serve_forever(self):
        raise NotImplementedError
