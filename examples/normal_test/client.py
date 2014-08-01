# -*- coding: utf-8 -*-


from netkit.stream import Stream
from reimp import Box

import time
import socket

address = ('127.0.0.1', 7777)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(address)

stream = Stream(s)

box = Box()
if hasattr(box, 'set_json'):
    box.set_json(dict(
        endpoint=101,
        body=u'我爱你'
    ))
else:
    box.cmd = 101
    box.body = '我爱你'

stream.write(box.pack())

t1 = time.time()

while True:
    # 阻塞
    buf = stream.read_with_checker(Box().check)

    print 'time past: ', time.time() - t1

    if buf:
        box2 = Box()
        box2.unpack(buf)
        print box2

    if stream.closed():
        print 'server closed'
        break

s.close()
