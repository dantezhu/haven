# -*- coding: utf-8 -*-

import json

from . import constants
from .request import Request
from .utils import safe_call
from .log import logger


class Connection(object):
    def __init__(self, app, stream, address, terminator=None, request_class=None):
        self.app = app
        self.stream = stream
        self.address = address
        self.terminator = terminator or '\n'
        self.request_class = request_class or Request

        self._clear_request_state()

        self.stream.set_close_callback(self._on_connection_close)

        self.app.events.create_conn(self)
        for name, bp in self.app.blueprints.items():
            bp.events.create_app_conn(self)

    def write(self, data, callback=None):
        """
        发送数据(实现是放到发送队列)
        """
        if isinstance(data, dict):
            data = self.make_rsp(**data)

        self.app.events.before_response(self, data)
        for name, bp in self.app.blueprints.items():
            bp.events.before_app_response(self, data)

        if not self.stream.closed():
            self._write_callback = callback
            self.stream.write(data, self._on_write_complete)

    def finish(self):
        """Finishes the request."""
        self._request_finished = True
        # No more data is coming, so instruct TCP to send any remaining
        # data immediately instead of waiting for a full packet or ack.
        self.stream.set_nodelay(True)
        if not self.stream.writing():
            self.close()

    def close(self, exc_info=False):
        """
        直接关闭连接
        注意: 不要在write完了之后直接调用，会导致write发送不出去(这个不太确定，tcp是全双工，理论上关闭了对方也会收到)
        """
        self.stream.close(exc_info)
        self._clear_request_state()

    def make_rsp(self, *args, **kwargs):
        """
        生成rsp
        """
        return json.dumps(dict(*args, **kwargs)) + self.terminator

    def set_close_callback(self, callback):
        """Sets a callback that will be run when the connection is closed.
        """
        self._close_callback = callback

    def process(self):
        """
        启动执行
        """
        # 开始等待数据
        self._read_message()

    def _on_connection_close(self):
        # 链接被关闭的回调
        logger.debug('socket closed')

        if self._close_callback is not None:
            callback = self._close_callback
            self._close_callback = None
            safe_call(callback)

        for name, bp in self.app.blueprints.items():
            bp.events.close_app_conn(self)
        self.app.events.close_conn(self)

    def _read_message(self):
        if not self.stream.closed():
            self.stream.read_until(self.terminator, self._on_read_complete)

    def _on_read_complete(self, raw_data):
        """
        数据获取结束
        """
        logger.debug('raw_data: %s', raw_data)
        request = self.request_class(self, raw_data)
        self._handle_request(request)

    def _on_write_complete(self):
        if self._write_callback is not None:
            callback = self._write_callback
            self._write_callback = None
            safe_call(callback)
        if self._request_finished and not self.stream.writing():
            self.close()

    def _clear_request_state(self):
        """Clears the per-request state.

        This is run in between requests to allow the previous handler
        to be garbage collected (and prevent spurious close callbacks),
        and when the connection is closed (to break up cycles and
        facilitate garbage collection in cpython).
        """
        self._request_finished = False
        self._write_callback = None
        self._close_callback = None

    def _handle_request(self, request):
        """
        出现任何异常的时候，服务器不再主动关闭连接
        """

        if not request.is_valid:
            request.write(dict(ret=constants.RET_SYSTEM, error='invalid request'))
            return None

        view_func = self.app.get_route_view_func(request.endpoint)
        if not view_func:
            if request.blueprint:
                view_func = request.blueprint.get_route_view_func(request.blueprint_endpoint)

        if not view_func:
            error = 'endpoint invalid. request: %s' % request
            logger.error(error)
            request.write(dict(ret=constants.RET_SYSTEM, error=error))
            return None

        if not self.app.got_first_request:
            self.app.got_first_request = True
            self.app.events.before_first_request(request)

            for name, bp in self.app.blueprints.items():
                bp.events.before_app_first_request(request)

        self.app.events.before_request(request)
        for name, bp in self.app.blueprints.items():
            bp.events.before_app_request(request)
        if request.blueprint:
            request.blueprint.events.before_request(request)

        view_func_exc = None
        view_func_result = None

        try:
            view_func_result = view_func(request)
        except Exception, e:
            error = 'view_func raise exception. request: %s, view_func: %s, e: %s, traceback: %s' % (
                request, view_func, e, __import__('traceback').format_exc())
            logger.error(error)
            view_func_exc = e
            request.write(dict(ret=constants.RET_SYSTEM,
                               error=error if self.app.debug else constants.ERROR_INTERNAL))

        if request.blueprint:
            request.blueprint.events.after_request(request, view_func_exc or view_func_result)

        for name, bp in self.app.blueprints.items():
            bp.events.after_app_request(request, view_func_exc or view_func_result)

        self.app.events.after_request(request, view_func_exc or view_func_result)

        return view_func_result
