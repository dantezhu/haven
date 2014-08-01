# -*- coding: utf-8 -*-

from .utils import safe_func
from events import Events


class RoutesMixin(object):
    """
    专门做路由管理
    """

    rule_map = None
    events = None

    def __init__(self):
        self.rule_map = dict()
        self.events = Events()

    def add_route_rule(self, cmd=None, view_func=None, **options):
        assert view_func is not None, 'expected view func if cmd is not provided.'

        cmd = cmd if cmd is not None else view_func.__name__

        if cmd in self.rule_map and view_func != self.rule_map[cmd]:
            raise Exception, 'duplicate view_func for cmd: %(cmd)s, old_view_func:%(old_view_func)s, new_view_func: %(new_view_func)s' % dict(
                cmd=cmd,
                old_view_func=self.rule_map[cmd],
                new_view_func=view_func,
            )

        self.rule_map[cmd] = view_func

    def route(self, cmd=None, **options):
        def decorator(f):
            self.add_route_rule(cmd, f, **options)
            return f
        return decorator

    def get_route_view_func(self, cmd):
        return self.rule_map.get(cmd)


class AppCallBacksMixin(RoutesMixin):

    def create_conn(self, f):
        """
        连接建立成功后
        f(conn)
        """
        self.events.create_conn += safe_func(f)
        return f

    def before_first_request(self, f):
        """
        第一个请求，请求解析为json成功后
        f(request)
        """
        self.events.before_first_request += safe_func(f)
        return f

    def before_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """
        self.events.before_request += safe_func(f)
        return f

    def after_request(self, f):
        """
        执行完route对应的view_func后
        f(request, exc)
        """
        self.events.after_request += safe_func(f)
        return f

    def before_response(self, f):
        """
        在 stream.write 之前，传入encode之后的data
        f(conn, response)
        """
        self.events.before_response += safe_func(f)
        return f

    def after_response(self, f):
        """
        在 stream.write 之后，传入encode之后的data
        f(conn, response)
        """
        self.events.after_response += safe_func(f)
        return f

    def close_conn(self, f):
        """
        连接close之后
        f(conn)
        """
        self.events.close_conn += safe_func(f)
        return f


class BlueprintCallBacksMixin(RoutesMixin):

    def before_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """
        self.events.before_request += safe_func(f)
        return f

    def after_request(self, f):
        """
        执行完route对应的view_func后
        f(request)
        """
        self.events.after_request += safe_func(f)
        return f

    def create_app_conn(self, f):
        """
        连接建立成功后
        f(conn)
        """
        self.events.create_app_conn += safe_func(f)
        return f

    def before_app_first_request(self, f):
        """
        第一次请求，请求解析为json成功后
        f(request)
        """
        self.events.before_app_first_request += safe_func(f)
        return f

    def before_app_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """
        self.events.before_app_request += safe_func(f)
        return f

    def after_app_request(self, f):
        """
        执行完route对应的view_func后
        f(request)
        """
        self.events.after_app_request += safe_func(f)
        return f

    def before_app_response(self, f):
        """
        在 stream.write 之前，传入encode之后的data
        f(conn, response)
        """
        self.events.before_app_response += safe_func(f)
        return f

    def after_app_response(self, f):
        """
        在 stream.write 之后，传入encode之后的data
        f(conn, response)
        """
        self.events.after_app_response += safe_func(f)
        return f

    def close_app_conn(self, f):
        """
        连接close之后
        f(conn)
        """
        self.events.close_app_conn += safe_func(f)
        return f
