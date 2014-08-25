# -*- coding: utf-8 -*-

from reimp import App, logger, Box

app = App(Box)


@app.route(1)
def index(request):
    request.write(dict(ret=0))

app.run('127.0.0.1', 7777, workers=2)
