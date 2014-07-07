# -*- coding: utf-8 -*-

import logging
from netkit.box import Box

from haven import THaven, logger
import user

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

app = THaven(Box)

@app.create_conn
def create_conn(conn):
    logger.error('create_conn')

@app.close_conn
def close_conn(conn):
    logger.error('close_conn')

@app.before_first_request
def before_first_request(request):
    logger.error('before_first_request')

@app.before_request
def before_request(request):
    logger.error('before_request')

@app.after_request
def after_request(request, exc):
    logger.error('after_request')

@app.before_response
def before_response(conn, rsp):
    logger.error('before_response: %r', rsp)

@app.after_response
def after_response(conn, rsp):
    logger.error('after_response: %r', rsp)

@app.route(1)
def index(request):
    from haven import TLater
    later = TLater()

    def x():
        logger.debug('x')
        later.set(1, y, repeat=True)

    def y():
        logger.debug('y')
        later.set(1, x, repeat=True)

    x()
    request.echo(ret=100)

app.register_blueprint(user.bp)
app.run('127.0.0.1', 7777)
