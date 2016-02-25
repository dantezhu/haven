# -*- coding: utf-8 -*-

from .log import logger


class Request(object):
    """
    请求
    """

    conn = None
    raw_data = None
    box = None
    is_valid = False
    blueprint = None
    route_rule = None
    # 是否中断处理，即不调用view_func，主要用在before_request中
    interrupted = False

    def __init__(self, conn, raw_data):
        self.conn = conn
        self.raw_data = raw_data
        self.is_valid = self._parse_raw_data()

    def _parse_raw_data(self):
        try:
            self.box = self.conn.app.box_class()
        except Exception, e:
            logger.error('parse raw_data fail. e: %s, request: %s', e, self)
            return False

        if self.box.unpack(self.raw_data) > 0:
            self._parse_route_rule()
            return True
        else:
            logger.error('unpack fail. request: %s', self)
            return False

    def _parse_route_rule(self):
        if self.cmd is None:
            return

        route_rule = self.app.get_route_rule(self.cmd)
        if route_rule:
            # 在app层，直接返回
            self.route_rule = route_rule
            return

        for bp in self.app.blueprints:
            route_rule = bp.get_route_rule(self.cmd)
            if route_rule:
                self.blueprint = bp
                self.route_rule = route_rule
                break

    @property
    def app(self):
        return self.conn.app

    @property
    def address(self):
        return self.conn.address

    @property
    def cmd(self):
        try:
            return self.box.cmd
        except:
            return None

    @property
    def view_func(self):
        return self.route_rule['view_func'] if self.route_rule else None

    @property
    def endpoint(self):
        if not self.route_rule:
            return None

        bp_endpoint = self.route_rule['endpoint']

        return '.'.join([self.blueprint.name, bp_endpoint] if self.blueprint else [bp_endpoint])

    def write(self, data):
        if isinstance(data, dict):
            # 生成box
            data = self.box.map(data)
        return self.conn.write(data)

    def close(self, exc_info=False):
        self.conn.close(exc_info)

    def interrupt(self, data=None):
        """
        中断处理
        :param data: 要响应的数据，不传即不响应
        :return:
        """
        self.interrupted = True
        if data is not None:
            return self.write(data)
        else:
            return True

    def __repr__(self):
        return 'client_address: %r, cmd: %r, endpoint: %s, raw_data: %r' % (
            self.address, self.cmd, self.endpoint, self.raw_data
        )
