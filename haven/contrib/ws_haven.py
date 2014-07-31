# -*- coding: utf-8 -*-

"""
websocket协议支持
"""

import re
import gevent.wsgi
from geventwebsocket.handler import WebSocketHandler
from netkit.stream import Stream
from .. import logger
from .. import GHaven


class WSStream(Stream):
    def read_from_fd(self):
        try:
            chunk = self.sock.receive()
        except:
            logger.error('exc occur.', exc_info=True)
            # 其他都直接关闭
            self.close()
            return None

        if not chunk:
            self.close()
            return None
        return chunk

    def write_to_fd(self, data):
        try:
            return self.sock.send(data)
        except:
            logger.error('exc occur.', exc_info=True)
            return None

    def close_fd(self):
        try:
            self.sock.close()
        finally:
            self.sock = None

    def shutdown_fd(self, how=2):
        try:
            self.sock.stream.handler.socket.shutdown(how)
        finally:
            pass


class WSHaven(GHaven):

    def __init__(self, path_pattern, merge_wsgi_app, *args, **kwargs):
        super(WSHaven, self).__init__(*args, **kwargs)
        self.path_pattern = path_pattern
        self.merge_wsgi_app = merge_wsgi_app

    def handle_stream(self, sock, address):
        self.connection_class(self, self.box_class, self.request_class, WSStream(sock), address).handle()

    def wsgi_app(self, environ, start_response):
        """
        将原始的app，包装为包括websocket的app
        """

        path = environ['PATH_INFO']

        if re.match(self.path_pattern, path):
            ws = environ['wsgi.websocket']
            address = environ.get('REMOTE_ADDR')
            self.handle_stream(ws, address)
        else:
            if self.merge_wsgi_app:
                return self.merge_wsgi_app(environ, start_response)
            else:
                start_response("400 Bad Request", [])
                return ['400 Bad Request']

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def _prepare_server(self, host, port):
        self.server = gevent.wsgi.WSGIServer((host, port), self.wsgi_app, handler_class=WebSocketHandler)

    def _serve_forever(self):
        self.server.serve_forever()