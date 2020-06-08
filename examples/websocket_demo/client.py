#!/usr/bin/env python
"""
pip install websocket-client
"""

from __future__ import print_function

import time

from websocket import create_connection
from websocket import ABNF
from reimp import Box

ws = create_connection("ws://127.0.0.1:8000/echo")
# ws = create_connection("ws://115.28.224.64:8000/echo")
box = Box()
box.cmd = 101
box.body = '我爱你'

t1 = time.time()
# 二进制协议
ws.send(box.pack(), ABNF.OPCODE_BINARY)
result = ws.recv()
print('time past: ', time.time() - t1)
print("Received '%r'" % result)
recv_box = Box()
recv_box.unpack(result)
print(recv_box)
ws.close()
