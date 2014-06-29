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

    def make_rsp(self, **kwargs):
        """
        生成rsp
        """
        rsp = self.box_class()
        for it in ['cmd', 'sn']:
            if hasattr(self.box, it):
                setattr(rsp, it, getattr(self.box, it))

        for k, v in kwargs:
            setattr(rsp, k, v)

        return rsp

    def echo(self, ret):
        """
        快速回复
        """
        box = self.make_rsp(ret=ret)

        self.write(box)

    def __repr__(self):
        return repr(self.raw_data)