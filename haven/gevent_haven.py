# -*- coding: utf-8 -*-


import gevent
from gevent.server import StreamServer
from netkit.stream import Stream

from .connection import Connection
from .haven import Haven


class GeventConnection(Connection):

    def _read_message(self):
        """
        必须启动新的greenlet，否则会有内存泄漏
        """
        job = gevent.spawn(super(GeventConnection, self)._read_message)
        job.join()


class GeventHaven(Haven):

    server = None

    def __init__(self, box_class, server_class=None, conn_class=None):
        super(GeventHaven, self).__init__()
        self.box_class = box_class
        self.server_class = server_class or StreamServer
        self.conn_class = conn_class or GeventConnection

    def handle_stream(self, sock, address):
        self.conn_class(self, self.box_class, Stream(sock), address).process()

    def run(self, host, port):
        self.server = self.server_class((host, port), self.handle_stream)

        self.server.serve_forever()