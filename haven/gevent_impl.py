# -*- coding: utf-8 -*-


import gevent
from gevent.server import StreamServer
import functools
from netkit.stream import Stream

from .connection import Connection
from .request import Request
from .haven import Haven
from .blueprint import Blueprint
from .utils import safe_call
from . import constants


class GConnection(Connection):

    def _read_message(self):
        """
        必须启动新的greenlet，否则会有内存泄漏
        """
        job = gevent.spawn(super(GConnection, self)._read_message)
        job.join()


class GHaven(Haven):

    server_class = StreamServer
    connection_class = GConnection
    request_class = Request
    stream_class = Stream

    box_class = None
    stream_checker = None

    backlog = constants.SERVER_BACKLOG
    server = None

    def __init__(self, box_class):
        super(GHaven, self).__init__()
        self.box_class = box_class
        self.stream_checker = self.box_class().check

    def _handle_stream(self, sock, address):
        if self.timeout is not None:
            sock.settimeout(self.timeout)
        self.connection_class(
            self, self.stream_class(sock, use_gevent=True), address
        ).handle()

    def repeat_timer(self, interval):
        def inner_repeat_timer(func):
            later = GTimer()
            self.events.repeat_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer

    def _prepare_server(self, address):
        import _socket
        # 只有这样，才能保证在主进程里面，不会启动accept
        listener = self.server_class.get_listener(address, backlog=self.backlog, family=_socket.AF_INET)
        self.server = self.server_class(listener, handle=self._handle_stream)

    def _serve_forever(self):
        self.server.serve_forever()


class GBlueprint(Blueprint):

    def repeat_app_timer(self, interval):
        def inner_repeat_timer(func):
            later = GTimer()
            self.events.repeat_app_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer


class GTimer(object):

    timer = None

    def set(self, interval, callback, repeat=False, force=True):
        """
        添加timer
        """
        if self.timer:
            if force:
                # 如果已经存在，那么先要把现在的清空
                self.clear()
            else:
                # 已经存在的话，就返回了
                return

        def callback_wrapper():
            # 必须要确定，这次调用就是这个timer引起的
            if self.timer == timer:
                # 必须加这句，否则如果在callback中有clear操作，会出现GreenletExit
                self.timer = None
                # 不可以加 timer = None，否则会导致判断self.timer == timer 报错找不到timer
                result = safe_call(callback)
                if repeat and not self.timer:
                    # 之所以还要判断timer，是因为callback中可能设置了新的回调
                    self.set(interval, callback, repeat, True)
                return result

        self.timer = timer = gevent.spawn_later(interval, callback_wrapper)

    def clear(self):
        """
        直接把现在的清空
        """
        if not self.timer:
            return

        # 不阻塞
        try:
            self.timer.kill(block=False)
        except:
            pass
        self.timer = None
