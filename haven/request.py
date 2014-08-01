# -*- coding: utf-8 -*-

import numbers
from .log import logger


class Request(object):
    """
    请求
    """

    conn = None
    box_class = None
    raw_data = None
    box = None
    is_valid = False
    blueprint = None
    blueprint_name = None
    blueprint_cmd = None

    def __init__(self, conn, box_class, raw_data):
        self.conn = conn
        self.box_class = box_class
        self.raw_data = raw_data
        self.is_valid = self._parse_raw_data()

    def _parse_raw_data(self):
        try:
            self.box = self.box_class()
        except Exception, e:
            logger.error('parse raw_data fail. e: %s, request: %s', e, self)
            return False

        if self.box.unpack(self.raw_data) > 0:
            self._parse_blueprint_info()
            return True
        else:
            logger.error('unpack fail. request: %s', self)
            return False

    def _parse_blueprint_info(self):
        if self.cmd is None:
            return

        cmd_parts = str(self.cmd).split('.')
        self.blueprint_name, self.blueprint_cmd = cmd_parts if len(cmd_parts) == 2 else (None, self.cmd)

        for bp in self.app.blueprints:
            if self.blueprint_name == bp.name or isinstance(self.blueprint_cmd, numbers.Number):
                # blueprint name 匹配; 或者cmd是数字类型，即与blueprint name无关
                if bp.get_route_view_func(self.blueprint_cmd):
                    self.blueprint = bp
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

    def write(self, data):
        if isinstance(data, dict):
            # 生成box
            data = self.box.map(data)
        return self.conn.write(data)

    def close(self, exc_info=False):
        self.conn.close(exc_info)

    def __repr__(self):
        return repr(self.raw_data)