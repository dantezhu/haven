"""
pip install gevent-websocket
"""

from __future__ import print_function

from gevent import monkey; monkey.patch_all()

from haven.contrib.websocket_gevent_impl import WSGHaven
from reimp import Box, logger
from flask import Flask

flask_app = Flask(__name__)


@flask_app.route('/http')
def http():
    return 'http ok'

app = WSGHaven(Box, '/echo', flask_app)


@app.route(101)
def index(request):
    request.write(dict(
        ret=1,
        body=repr(request.address),
    ))


@app.repeat_timer(60)
def timer():
    logger.debug('timer')


if __name__ != '__main__':
    # 启动timer之类的
    app._on_worker_start()

if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
