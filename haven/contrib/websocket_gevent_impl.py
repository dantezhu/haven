# -*- coding: utf-8 -*-

"""
websocket协议支持
"""

import re
import gevent.wsgi
from geventwebsocket.handler import WebSocketHandler
from netkit.stream import Stream
from haven import logger
from haven import GHaven


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

        # 如果二进制传输，获取的将会是bytearray，会导致box.body是bytearray格式，从而导致protobuf parse报错
        return str(chunk)

    def write_to_fd(self, data):
        try:
            return self.sock.send(data)
        except:
            logger.error('exc occur. data: %r', data, exc_info=True)
            return None

    def close_fd(self):
        try:
            self.sock.close()
        except:
            logger.error('exc occur.', exc_info=True)
        finally:
            self.sock = None

    def shutdown_fd(self, how=2):
        try:
            self.sock.stream.handler.socket.shutdown(how)
        except:
            logger.error('exc occur.', exc_info=True)


class WSGHaven(GHaven):

    def __init__(self, box_class, path_pattern, merge_wsgi_app=None, **kwargs):
        # 去掉*args，即可避免stream_class在*args的情况
        if not kwargs.get('stream_class'):
            kwargs['stream_class'] = WSStream
        super(WSGHaven, self).__init__(box_class, **kwargs)

        self.path_pattern = path_pattern
        self.merge_wsgi_app = merge_wsgi_app

    def wsgi_app(self, environ, start_response):
        """
        将原始的app，包装为包括websocket的app
        """

        path = environ['PATH_INFO']

        if re.match(self.path_pattern, path):
            ws = environ['wsgi.websocket']
            address = (environ.get('REMOTE_ADDR'), environ.get('REMOTE_PORT'))
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
        self.server = gevent.wsgi.WSGIServer((host, port), self.wsgi_app,
                                             backlog=self.backlog, handler_class=WebSocketHandler)
        self.server.start()

    def _serve_forever(self):
        self.server.serve_forever()