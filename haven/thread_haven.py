# -*- coding: utf-8 -*-

import functools
import thread
import time
from SocketServer import ThreadingTCPServer, StreamRequestHandler
from netkit.stream import Stream

from .utils import safe_call
from .connection import Connection
from .haven import Haven


class ThreadHaven(Haven):

    server = None

    def __init__(self, box_class, server_class=None, conn_class=None):
        super(ThreadHaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or ThreadingTCPServer
        self.conn_class = conn_class or Connection

    def handle_stream(self, sock, address):
        self.conn_class(self, self.box_class, Stream(sock), address).process()

    def run(self, host, port):

        class RequestHandler(StreamRequestHandler):
            def handle(sub_self):
                self.conn_class(self, self.box_class, Stream(sub_self.connection), sub_self.client_address).process()

        self.server = self.server_class((host, port), RequestHandler)

        self._start_repeat_timers()
        self.server.serve_forever()

    def repeat_timer(self, interval):
        """
        每隔一段时间执行(秒)
        """
        def inner_repeat_timer(func):
            @functools.wraps(func)
            def func_wrapper(*args, **kwargs):
                # 每次也要再加入

                time.sleep(interval)
                result = safe_call(func, *args, **kwargs)

                thread.start_new_thread(func_wrapper, ())

                return result

            self.events.repeat_timer += functools.partial(thread.start_new_thread, func_wrapper, ())
            return func_wrapper
        return inner_repeat_timer

    def _start_repeat_timers(self):
        """
        把那些repeat timers启动
        """
        self.events.repeat_timer()
