# -*- coding: utf-8 -*-

from SocketServer import ThreadingTCPServer, StreamRequestHandler
import threading
import functools
from netkit.stream import Stream

from .connection import Connection
from .request import Request
from .haven import Haven
from .blueprint import Blueprint
from .utils import safe_call


class THaven(Haven):

    server = None

    def __init__(self, box_class, server_class=None, conn_class=None, request_class=None):
        super(THaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or ThreadingTCPServer
        self.conn_class = conn_class or Connection
        self.request_class = request_class or Request

    def run(self, host, port):

        class RequestHandler(StreamRequestHandler):
            def handle(sub_self):
                self.conn_class(
                    self, self.box_class, self.request_class, Stream(sub_self.connection), sub_self.client_address
                ).process()

        self.server = self.server_class((host, port), RequestHandler, bind_and_activate=False)
        # 主线程退出时，所有子线程结束
        self.server.daemon_threads = True
        # 必须在server_bind之前
        self.server.allow_reuse_address = True

        self.server.server_bind()
        self.server.server_activate()

        self._start_repeat_timers()

        self.server.serve_forever()

    def repeat_timer(self, interval):
        def inner_repeat_timer(func):
            later = TLater()
            self.events.repeat_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer

    def _start_repeat_timers(self):
        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()


class TBlueprint(Blueprint):

    def repeat_app_timer(self, interval):
        def inner_repeat_timer(func):
            later = TLater()
            self.events.repeat_app_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer


class TLater(object):

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

        self.timer = timer = threading.Timer(interval, callback_wrapper)
        # 跟着主线程结束。默认值是和创建的线程一致
        timer.daemon = True
        timer.start()

    def clear(self):
        """
        直接把现在的清空
        """
        if not self.timer:
            return

        self.timer.cancel()
        self.timer = None
