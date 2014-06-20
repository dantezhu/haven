# -*- coding: utf-8 -*-

from netkit.box import Box

from haven.thread_haven import ThreadHaven

app = ThreadHaven(Box)


@app.route(1)
def index(request):
    request.feedback(100)

app.run('127.0.0.1', 7777)
