# -*- coding: utf-8 -*-

from reimp import Haven, logger, Box

app = Haven(Box)


@app.route(1)
def index(request):
    request.write(dict(ret=0))

app.run('127.0.0.1', 7777, workers=4)
