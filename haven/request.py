# -*- coding: utf-8 -*-

import copy
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

    def feedback(self, ret):
        """
        快速回复
        """
        box = copy.deepcopy(self.box)
        # 清空body
        box.body = ''
        box.ret = ret

        self.write(box)

    def __repr__(self):
        return repr(self.raw_data)