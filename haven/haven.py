# -*- coding: utf-8 -*-

import sys
from multiprocessing import Process
import time
import signal
from collections import Counter
import setproctitle

from .mixins import RoutesMixin, AppEventsMixin
from .log import logger
from . import constants


class Haven(RoutesMixin, AppEventsMixin):
    ############################## configurable begin ##############################
    name = constants.NAME
    ############################## configurable end   ##############################

    enable = True
    processes = None
    debug = False
    got_first_request = False
    blueprints = None

    def __init__(self):
        RoutesMixin.__init__(self)
        AppEventsMixin.__init__(self)
        self.processes = []
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register_to_app(self)

    def run(self, host=None, port=None, debug=None, workers=None):
        """
        启动
        :param host: 监听IP
        :param port: 监听端口
        :param debug: 是否debug
        :param workers: workers数量
        :return:
        """
        self._validate_cmds()

        if host is None:
            host = constants.SERVER_HOST
        if port is None:
            port = constants.SERVER_PORT
        if debug is not None:
            self.debug = debug

        workers = workers if workers is not None else 1

        logger.info('Running server on %s:%s, debug: %s, workers: %s',
                    host, port, self.debug, workers)

        self._prepare_server((host, port))
        setproctitle.setproctitle(self._make_proc_name('master'))
        # 只能在主线程里面设置signals
        self._handle_parent_proc_signals()
        self._spawn_workers(workers, self._worker_run)

    def acquire_got_first_request(self):
        pass

    def release_got_first_request(self):
        pass

    def repeat_timer(self, interval):
        raise NotImplementedError

    def _make_proc_name(self, subtitle):
        """
        获取进程名称
        :param subtitle:
        :return:
        """
        proc_name = '[%s:%s %s] %s' % (
            constants.NAME,
            subtitle,
            self.name,
            ' '.join([sys.executable] + sys.argv)
        )

        return proc_name

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

    def _on_worker_run(self):
        self.events.create_worker()
        for bp in self.blueprints:
            bp.events.create_app_worker()

        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()

    def _worker_run(self):
        setproctitle.setproctitle(self._make_proc_name('worker'))
        self._handle_child_proc_signals()

        self._on_worker_run()

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)

    def _spawn_workers(self, workers, target):
        def start_worker_process():
            inner_p = Process(target=target)
            # 当前进程daemon默认是False，改成True将启动不了子进程
            # 但是子进程要设置daemon为True，这样父进程退出，子进程会被强制关闭
            # 现在父进程会在子进程之后退出，没必要设置了
            # inner_p.daemon = True
            inner_p.start()
            return inner_p

        for it in xrange(0, workers):
            p = start_worker_process()
            self.processes.append(p)

        while 1:
            for idx, p in enumerate(self.processes):
                if p and not p.is_alive():
                    self.processes[idx] = None

                    if self.enable:
                        p = start_worker_process()
                        self.processes[idx] = p

            if not filter(lambda x: x, self.processes):
                # 没活着的了
                break

            # 时间短点，退出的快一些
            time.sleep(0.1)

    def _handle_parent_proc_signals(self):
        def exit_handler(signum, frame):
            self.enable = False

            # 如果是终端直接CTRL-C，子进程自然会在父进程之后收到INT信号，不需要再写代码发送
            # 如果直接kill -INT $parent_pid，子进程不会自动收到INT
            # 所以这里可能会导致重复发送的问题，重复发送会导致一些子进程异常，所以在子进程内部有做重复处理判断。
            for p in self.processes:
                if p:
                    p.terminate()

        # INT, QUIT, TERM为强制结束
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGQUIT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

    def _handle_child_proc_signals(self):
        def exit_handler(signum, frame):
            # 防止重复处理KeyboardInterrupt，导致抛出异常
            if self.enable:
                self.enable = False
                raise KeyboardInterrupt

        # 强制结束，抛出异常终止程序进行
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGQUIT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

    def _prepare_server(self, address):
        raise NotImplementedError

    def _serve_forever(self):
        raise NotImplementedError
