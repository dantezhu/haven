# -*- coding: utf-8 -*-

from .mixins import RoutesMixin, BlueprintEventsMixin


class Blueprint(RoutesMixin, BlueprintEventsMixin):

    name = None
    app = None

    def __init__(self, name=None):
        RoutesMixin.__init__(self)
        BlueprintEventsMixin.__init__(self)
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
