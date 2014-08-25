# -*- coding: utf-8 -*-

from . import constants
from .log import logger


class Connection(object):
    def __init__(self, app, box_class, request_class, stream, address):
        self.app = app
        self.box_class = box_class
        self.request_class = request_class
        self.stream = stream
        self.address = address

        self.app.events.create_conn(self)
        for bp in self.app.blueprints:
            bp.events.create_app_conn(self)

    def write(self, data):
        """
        发送数据    True: 成功   else: 失败
        """
        if self.stream.closed():
            return

        if isinstance(data, self.box_class):
            # 打包
            data = data.pack()
        elif isinstance(data, dict):
            data = self.box_class(data).pack()

        self.app.events.before_response(self, data)
        for bp in self.app.blueprints:
            bp.events.before_app_response(self, data)

        ret = self.stream.write(data)

        for bp in self.app.blueprints:
            bp.events.after_app_response(self, data, ret)
        self.app.events.after_response(self, data, ret)

        return ret

    def close(self, exc_info=False):
        """
        直接关闭连接
        """
        self.stream.close(exc_info)

    def closed(self):
        """
        连接是否已经关闭
        :return:
        """
        return self.stream.closed()

    def handle(self):
        """
        启动处理
        """
        # while中判断可以保证connection_close事件只触发一次
        while not self.stream.closed():
            self._read_message()

    def _read_message(self):
        data = self.stream.read_with_checker(self.box_class.instance().check)
        if data:
            self._on_read_complete(data)

        # 在这里加上判断，因为如果在处理函数里关闭了conn，会导致无法触发on_connction_close
        if self.stream.closed():
            self._on_connection_close()

    def _on_connection_close(self):
        # 链接被关闭的回调

        for bp in self.app.blueprints:
            bp.events.close_app_conn(self)
        self.app.events.close_conn(self)

    def _on_read_complete(self, data):
        """
        数据获取结束
        """
        request = self.request_class(self, self.box_class, data)
        self._handle_request(request)

    def _handle_request(self, request):
        """
        出现任何异常的时候，服务器不再主动关闭连接
        """

        if not request.is_valid:
            return None

        view_func = self.app.get_route_view_func(request.cmd)
        if not view_func and request.blueprint:
            view_func = request.blueprint.get_route_view_func(request.blueprint_cmd)

        if not view_func:
            logger.error('cmd invalid. request: %s' % request)
            request.write(dict(ret=constants.RET_INVALID_CMD))
            return None

        if not self.app.got_first_request:
            real_got_first_request = False

            # 加锁
            self.app.acquire_got_first_request()
            if not self.app.got_first_request:
                self.app.got_first_request = True
                real_got_first_request = True
            self.app.release_got_first_request()

            if real_got_first_request:
                self.app.events.before_first_request(request)
                for bp in self.app.blueprints:
                    bp.events.before_app_first_request(request)

        self.app.events.before_request(request)
        for bp in self.app.blueprints:
            bp.events.before_app_request(request)
        if request.blueprint:
            request.blueprint.events.before_request(request)

        view_func_exc = None
        view_func_result = None

        try:
            view_func_result = view_func(request)
        except Exception, e:
            logger.error('view_func raise exception. request: %s, view_func: %s, e: %s',
                         request, view_func, e, exc_info=True)
            view_func_exc = e
            request.write(dict(ret=constants.RET_INTERNAL))

        if request.blueprint:
            request.blueprint.events.after_request(request, view_func_exc or view_func_result)
        for bp in self.app.blueprints:
            bp.events.after_app_request(request, view_func_exc or view_func_result)
        self.app.events.after_request(request, view_func_exc or view_func_result)

        return view_func_result
