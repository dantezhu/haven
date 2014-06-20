# -*- coding: utf-8 -*-

from gevent.server import StreamServer

from base import BaseHaven


class Connection(kola.connection.Connection):

    def process(self):
        while not self.stream.closed():
            self._read_message()

    def _read_message(self):
        # 按照官方文档，greenlet在存活的时候，是不参与内存回收的
        # 只有greenlet在释放的时候，所有引用才会释放

        job = gevent.spawn(self.stream.read_until, self.terminator, self._on_read_complete)
        job.join()


class GeventHaven(BaseHaven):

    server = None

    def __init__(self, server_class=None, conn_class=None):
        super(GeventHaven, self).__init__()
        self.server_class = server_class or StreamServer
        self.conn_class = conn_class or Connection

    def handle_stream(self, sock, address):
        self.conn_class(self, Stream(sock), address).process()

    def run(self, host, port, patch_all=True):
        if patch_all:
            from gevent import monkey
            monkey.patch_all()

        self.server = self.server_class((host, port), self.handle_stream)

        self._start_repeat_timers()
        self.server.serve_forever()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)

    def repeat_timer(self, interval):
        """
        每隔一段时间执行(秒)
        """
        def inner_repeat_timer(func):
            @functools.wraps(func)
            def func_wrapper(*args, **kwargs):
                # 每次也要再加入

                result = safe_call(func, *args, **kwargs)
                gevent.spawn_later(interval, func_wrapper)

                return result

            self.events.repeat_timer += functools.partial(gevent.spawn_later, interval, func_wrapper)
            return func_wrapper
        return inner_repeat_timer

    def _start_repeat_timers(self):
        """
        把那些repeat timers启动
        """
        self.events.repeat_timer()
        for name, bp in self.blueprints.items():
            bp.events.repeat_app_timer()
