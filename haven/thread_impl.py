# -*- coding: utf-8 -*-

from SocketServer import ThreadingTCPServer, StreamRequestHandler
import threading
import functools
from threading import Lock
from netkit.stream import Stream

from .connection import Connection
from .request import Request
from .haven import Haven
from .blueprint import Blueprint
from .utils import safe_call
from . import constants


class THaven(Haven):

    backlog = constants.SERVER_BACKLOG
    server = None
    got_first_request_lock = None

    def __init__(self, box_class, server_class=None, connection_class=None, request_class=None, stream_class=None):
        super(THaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or ThreadingTCPServer
        self.connection_class = connection_class or Connection
        self.request_class = request_class or Request
        self.stream_class = stream_class or Stream
        self.got_first_request_lock = Lock()

    def repeat_timer(self, interval):
        def inner_repeat_timer(func):
            later = TTimer()
            self.events.repeat_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer

    def acquire_got_first_request(self):
        self.got_first_request_lock.acquire()

    def release_got_first_request(self):
        self.got_first_request_lock.release()

    def _prepare_server(self, host, port):
        class RequestHandler(StreamRequestHandler):
            def handle(sub_self):
                self.connection_class(
                    self, self.box_class, self.request_class, self.stream_class(sub_self.connection), sub_self.client_address
                ).handle()

        self.server = self.server_class((host, port), RequestHandler, bind_and_activate=False)
        self.server.request_queue_size = self.backlog
        # 主线程退出时，所有子线程结束
        self.server.daemon_threads = True
        # 必须在server_bind之前
        self.server.allow_reuse_address = True

        self.server.server_bind()
        self.server.server_activate()

    def _serve_forever(self):
        self.server.serve_forever()


class TBlueprint(Blueprint):

    def repeat_app_timer(self, interval):
        def inner_repeat_timer(func):
            later = TTimer()
            self.events.repeat_app_timer += functools.partial(later.set, interval, func, True)
            return func

        return inner_repeat_timer


class TTimer(object):

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
                self.timer = None
                result = safe_call(callback)
                if repeat and not self.timer:
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

        try:
            self.timer.cancel()
        except:
            pass
        self.timer = None
