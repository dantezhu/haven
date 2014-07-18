# -*- coding: utf-8 -*-

from .callbacks_mixin import BlueprintCallBacksMixin


class Blueprint(BlueprintCallBacksMixin):

    name = None
    app = None

    def __init__(self, name=None):
        super(Blueprint, self).__init__()
        self.name = name

    def register2app(self, app):
        """
        注册到app上
        """
        self.app = app
        # 注册上
        self.app.blueprints.append(self)

    def repeat_app_timer(self, interval):
        raise NotImplementedError
