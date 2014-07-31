# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

from haven.contrib.ws_haven import WSHaven
from kola_box import KolaBox

app = WSHaven('/echo', None, KolaBox)


@app.route(1)
def index(request):
    print repr(request)
    request.write(dict(
        ret=1,
        body='ok haha'
    ))

if __name__ == '__main__':
    app.run('127.0.0.1', 8000)
