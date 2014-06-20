# -*- coding: utf-8 -*-

import logging

from gevent import monkey;monkey.patch_all()
from netkit.box import Box

from haven.gevent_haven import GeventHaven
from haven.log import logger

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


app = GeventHaven(Box)


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
    logger.error('rsp: %s', rsp)

@app.after_response
def after_response(conn, rsp):
    logger.error('rsp: %s', rsp)

@app.repeat_timer(5)
def repeat_timer():
    logger.error('repeat_timer')


@app.route(1)
def index(request):
    request.feedback(100)

app.run('127.0.0.1', 7777)
