#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from websocket import create_connection
from kola_box import KolaBox

ws = create_connection("ws://127.0.0.1:8000/echo")
# ws = create_connection("ws://115.28.224.64:8000/echo")
box = KolaBox()
box.set_json(dict(
    endpoint=1
))
t1 = time.time()
ws.send(box.pack())
result = ws.recv()
print 'time past: ', time.time() - t1
print "Received '%r'" % result
ws.close()