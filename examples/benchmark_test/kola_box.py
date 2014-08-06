# -*- coding: utf-8 -*-

from netkit.line_box import LineBox


class KolaBox(LineBox):

    def __init__(self, init_data=None):
        # 不要让顶层初始化init_data
        super(KolaBox, self).__init__(None)

        if init_data:
            self.set_json(init_data)

    @property
    def values(self):
        if not getattr(self, '_values', None):
            # 只赋值一次免得性能太低
            try:
                self._values = self.get_json()
            except:
                self._values = None

        return self._values

    @property
    def cmd(self):
        return self.values.get('endpoint', None)

    @property
    def sn(self):
        return self.values.get('sn', 0)

    def map(self, map_data):
        init_data = dict(
            endpoint=self.cmd,
            sn=self.sn,
        )
        init_data.update(map_data)

        return self.__class__(init_data)

