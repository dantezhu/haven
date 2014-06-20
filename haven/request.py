# -*- coding: utf-8 -*-

from .log import logger


class Request(object):
    """
    请求
    """

    box_class = None
    conn = None
    raw_data = None
    box = None
    is_valid = False

    def __init__(self, box_class, conn, raw_data):
        self.box_class = box_class

        # 为了书写方便
        self.finish = conn.finish
        self.close = conn.close

        self.conn = conn
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
            return False

    def write(self, data, *args, **kwargs):
        if isinstance(data, self.box_class):
            # 打包
            data = data.pack()

        return self.conn.write(data, *args, **kwargs)

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
    def sn(self):
        try:
            return self.box.sn
        except:
            return None

    def __repr__(self):
        return repr(self.raw_data)