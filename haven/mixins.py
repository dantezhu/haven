import functools
from events import Events

from .utils import safe_func


class RoutesMixin(object):
    """
    专门做路由管理
    """

    rule_map = None

    def __init__(self):
        self.rule_map = dict()

    def add_route_rule(self, cmd, view_func, endpoint=None, **kwargs):
        old_rule = self.rule_map.get(cmd)
        if old_rule and view_func != old_rule['view_func']:
            raise Exception(
                'duplicate view_func for cmd: {cmd}'.format(cmd=cmd)
            )

        rule = dict(
            endpoint=endpoint or view_func.__name__,
            view_func=view_func,
        )
        rule.update(kwargs)

        self.rule_map[cmd] = rule

    def route(self, cmd, endpoint=None, **kwargs):
        def decorator(func):
            self.add_route_rule(cmd, func, endpoint, **kwargs)
            return func
        return decorator

    def get_route_rule(self, cmd):
        return self.rule_map.get(cmd)


def _reg_event_handler(func):
    @functools.wraps(func)
    def func_wrapper(obj, handler):
        event = getattr(obj.events, func.__name__)
        event += safe_func(handler)

        return handler
    return func_wrapper


class AppEventsMixin(object):
    events = None

    def __init__(self):
        self.events = Events()

    @_reg_event_handler
    def start_worker(self, f):
        """
        创建worker
        f()
        """

    @_reg_event_handler
    def create_conn(self, f):
        """
        连接建立成功后
        f(conn)
        """

    @_reg_event_handler
    def before_first_request(self, f):
        """
        第一个请求，请求解析为json成功后
        f(request)
        """

    @_reg_event_handler
    def before_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """

    @_reg_event_handler
    def after_request(self, f):
        """
        执行完route对应的view_func后
        f(request, exc)
        """

    @_reg_event_handler
    def before_response(self, f):
        """
        在 stream.write 之前，传入encode之后的data
        f(conn, response)
        """

    @_reg_event_handler
    def after_response(self, f):
        """
        在 stream.write 之后，传入encode之后的data
        f(conn, response, result)
        """

    @_reg_event_handler
    def close_conn(self, f):
        """
        连接close之后
        f(conn)
        """

    @_reg_event_handler
    def stop_worker(self, f):
        """
        停止worker
        f()
        """


class BlueprintEventsMixin(object):

    events = None

    def __init__(self):
        self.events = Events()

    @_reg_event_handler
    def before_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """

    @_reg_event_handler
    def after_request(self, f):
        """
        执行完route对应的view_func后
        f(request, exc)
        """

    @_reg_event_handler
    def start_app_worker(self, f):
        """
        创建worker
        f()
        """

    @_reg_event_handler
    def create_app_conn(self, f):
        """
        连接建立成功后
        f(conn)
        """

    @_reg_event_handler
    def before_app_first_request(self, f):
        """
        第一次请求，请求解析为json成功后
        f(request)
        """

    @_reg_event_handler
    def before_app_request(self, f):
        """
        请求解析为json成功后
        f(request)
        """

    @_reg_event_handler
    def after_app_request(self, f):
        """
        执行完route对应的view_func后
        f(request, exc)
        """

    @_reg_event_handler
    def before_app_response(self, f):
        """
        在 stream.write 之前，传入encode之后的data
        f(conn, response)
        """

    @_reg_event_handler
    def after_app_response(self, f):
        """
        在 stream.write 之后，传入encode之后的data
        f(conn, response, result)
        """

    @_reg_event_handler
    def close_app_conn(self, f):
        """
        连接close之后
        f(conn)
        """

    @_reg_event_handler
    def stop_app_worker(self, f):
        """
        停止worker
        f()
        """
