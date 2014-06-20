# -*- coding: utf-8 -*-

from gevent import monkey;monkey.patch_all()
from netkit.box import Box

from haven.gevent_haven import GeventHaven

app = GeventHaven(Box)


@app.route(1)
def index(request):
    request.feedback(100)

app.run('127.0.0.1', 7777)
