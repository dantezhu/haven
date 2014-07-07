# -*- coding: utf-8 -*-

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

    def __init__(self, conn, box_class, raw_data):
        # 为了书写方便
        self.close = conn.close
        self.write = conn.write

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
            return True
        else:
            logger.error('unpack fail. request: %s', self)
            return False

    @property
    def app(self):
        return self.conn.app

    @property
    def blueprint(self):
        cmd_parts = str(self.cmd or '').split('.')
        bp_prefix, cmd = cmd_parts if len(cmd_parts) == 2 else (None, self.cmd)

        for bp in self.app.blueprints:
            if bp_prefix == bp.prefix and bp.get_route_view_func(cmd):
                return bp

        return None

    @property
    def blueprint_cmd(self):
        cmd_parts = str(self.cmd or '').split('.')
        return cmd_parts[1] if len(cmd_parts) == 2 else self.cmd

    @property
    def address(self):
        return self.conn.address

    @property
    def cmd(self):
        try:
            return self.box.cmd
        except:
            return None

    def make_rsp(self, **kwargs):
        """
        生成响应
        """
        assert self.box is not None

        return self.box.map(**kwargs)

    def echo(self, **kwargs):
        """
        快速响应
        """
        self.write(self.make_rsp(**kwargs))

    def __repr__(self):
        return repr(self.raw_data)