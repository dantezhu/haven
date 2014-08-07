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

    backlog = constants.SERVER_BACKLOG
    server = None

    def __init__(self, box_class, server_class=None, connection_class=None, request_class=None, stream_class=None):
        super(GHaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or StreamServer
        self.connection_class = connection_class or GConnection
        self.request_class = request_class or Request
        self.stream_class = stream_class or Stream

    def handle_stream(self, sock, address):
        self.connection_class(
            self, self.box_class, self.request_class, self.stream_class(sock, use_gevent=True), address
        ).handle()

    def repeat_timer(self, interval):
        def inner_repeat_timer(func):
            later = GTimer()
            self.events.repeat_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer

    def _prepare_server(self, host, port):
        self.server = self.server_class((host, port), handle=self.handle_stream, backlog=self.backlog)
        self.server.start()

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
