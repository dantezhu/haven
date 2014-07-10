# -*- coding: utf-8 -*-

from haven.request import Request


class KolaRequest(Request):

    @property
    def values(self):
        assert self.box is not None

        return self.box.values
