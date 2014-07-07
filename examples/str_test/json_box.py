# -*- coding: utf-8 -*-

from netkit.line_box import LineBox


class JsonBox(LineBox):

    def __init__(self, init_data=None):
        # 不要让顶层初始化init_data
        super(JsonBox, self).__init__(None)

        if init_data:
            self.set_json(init_data)

    @property
    def cmd(self):
        values = self.get_json()
        if not values:
            return None

        return values.get('endpoint', None)

    def map(self, map_data):
        init_data = dict(
            endpoint=self.cmd,
        )
        init_data.update(map_data)

        return self.__class__(init_data)
