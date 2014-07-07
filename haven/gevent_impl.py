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


class GConnection(Connection):

    def _read_message(self):
        """
        必须启动新的greenlet，否则会有内存泄漏
        """
        job = gevent.spawn(super(GConnection, self)._read_message)
        job.join()


class GHaven(Haven):

    server = None

    def __init__(self, box_class, server_class=None, conn_class=None, request_class=None):
        super(GHaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or StreamServer
        self.conn_class = conn_class or GConnection
        self.request_class = request_class or Request

    def handle_stream(self, sock, address):
        self.conn_class(self, self.box_class, self.request_class, Stream(sock), address).process()

    def run(self, host, port):
        self.server = self.server_class((host, port), self.handle_stream)

        self._start_repeat_timers()

        self.server.serve_forever()

    def repeat_timer(self, interval):
        def inner_repeat_timer(func):
            later = GLater()
            self.events.repeat_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer

    def _start_repeat_timers(self):
        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()


class GBlueprint(Blueprint):

    def repeat_app_timer(self, interval):
        def inner_repeat_timer(func):
            later = GLater()
            self.events.repeat_app_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer


class GLater(object):

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
                result = safe_call(callback)
                if repeat and self.timer == timer:
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
        self.timer.kill(block=False)
        self.timer = None
