from .log import logger


class Request(object):
    """
    请求
    """

    conn = None
    raw_data = None
    box = None
    is_valid = False
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
        except Exception as e:
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

        self.route_rule = self.app.get_route_rule(self.cmd)

    @property
    def cmd(self):
        return self.box.cmd if self.box else None

    @property
    def view_func(self):
        return self.route_rule['view_func'] if self.route_rule else None

    @property
    def endpoint(self):
        return self.route_rule['endpoint'] if self.route_rule else None

    @property
    def blueprint(self):
        return self.route_rule.get('blueprint') if self.route_rule else None

    @property
    def app(self):
        return self.conn.app

    @property
    def address(self):
        return self.conn.address

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
        return '<%s cmd: %r, endpoint: %s>' % (
            type(self).__name__, self.cmd, self.endpoint
        )
