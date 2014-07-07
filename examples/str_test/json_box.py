# -*- coding: utf-8 -*-

from netkit.line_box import LineBox


class JsonBox(LineBox):

    @property
    def cmd(self):
        values = self.get_json()
        if not values:
            return None

        return values.get('endpoint')

    def map(self, **kwargs):
        box = JsonBox()
        values = dict(
            endpoint=self.cmd,
        )
        values.update(kwargs)

        box.set_json(values)

        return box
