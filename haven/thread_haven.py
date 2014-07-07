# -*- coding: utf-8 -*-

from SocketServer import ThreadingTCPServer, StreamRequestHandler
from netkit.stream import Stream

from .connection import Connection
from .haven import Haven


class ThreadHaven(Haven):

    allow_reuse_address = True
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

        self.server.serve_forever()