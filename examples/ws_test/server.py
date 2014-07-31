# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

from haven.contrib.ws_haven import WSHaven
from kola_box import KolaBox
from flask import Flask

flask_app = Flask(__name__)


@flask_app.route('/http')
def http():
    return u'http ok'

app = WSHaven('/echo', flask_app, KolaBox)


@app.route(1)
def index(request):
    print repr(request)
    request.write(dict(
        ret=1,
        body='ok haha'
    ))

if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
