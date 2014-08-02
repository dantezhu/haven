#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from websocket import create_connection
from reimp import Box

ws = create_connection("ws://127.0.0.1:8000/echo")
# ws = create_connection("ws://115.28.224.64:8000/echo")
box = Box()
if hasattr(box, 'set_json'):
    box.set_json(dict(
        endpoint=101,
        body=u'我爱你'
    ))
else:
    box.cmd = 101
    box.body = '我爱你'

t1 = time.time()
ws.send(box.pack())
result = ws.recv()
print 'time past: ', time.time() - t1
print "Received '%r'" % result
ws.close()
