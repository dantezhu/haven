# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '../../')
import logging

from reimp import Haven, logger, Box
import user

app = Haven(Box)

@app.create_worker
def create_worker():
    logger.error('create_worker')

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
def after_response(conn, rsp, result):
    logger.error('after_response: %r, %s', rsp, result)


@app.repeat_timer(5)
def repeat_timer():
    logger.error('repeat_timer')


@app.route(1)
def index(request):
    logger.error('request: %s', request)
    request.write(dict(ret=100))


@app.route(2)
def repeat(request):
    from haven import TTimer
    timer = TTimer()

    def x():
        logger.debug('x')
        timer.set(1, y, repeat=True)

    def y():
        logger.debug('y')
        timer.set(1, x, repeat=True)

    # x()
    request.write(dict(ret=100))

app.register_blueprint(user.bp)
app.run('127.0.0.1', 7777, debug=True)
