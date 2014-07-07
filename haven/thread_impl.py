# -*- coding: utf-8 -*-

from SocketServer import ThreadingTCPServer, StreamRequestHandler
import threading
from netkit.stream import Stream

from .connection import Connection
from .haven import Haven
from .utils import safe_call


class THaven(Haven):

    server = None

    def __init__(self, box_class, server_class=None, conn_class=None):
        super(THaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or ThreadingTCPServer
        self.conn_class = conn_class or Connection

    def handle_stream(self, sock, address):
        self.conn_class(self, self.box_class, Stream(sock), address).process()

    def run(self, host, port):

        class RequestHandler(StreamRequestHandler):
            def handle(sub_self):
                self.conn_class(self, self.box_class, Stream(sub_self.connection), sub_self.client_address).process()

        self.server = self.server_class((host, port), RequestHandler, bind_and_activate=False)
        # 主线程退出时，所有子线程结束
        self.server.daemon_threads = True
        # 必须在server_bind之前
        self.server.allow_reuse_address = True

        self.server.server_bind()
        self.server.server_activate()

        self.server.serve_forever()


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

            # 这样可以让timer及时变成None
            if self.timer == timer:
                # 必须要确定，这次调用就是这个timer引起的
                self.timer = None
                result = safe_call(callback)
                if repeat:
                    # 重复的调用
                    self.set(interval, callback, repeat, force)
                return result

        self.timer = timer = threading.Timer(interval, callback_wrapper)
        timer.start()

    def clear(self):
        """
        直接把现在的清空
        """
        if not self.timer:
            return

        self.timer.cancel()
        self.timer = None
