# -*- coding: utf-8 -*-


from kola_box import KolaBox
from netkit.stream import Stream

import logging
import socket

logger = logging.getLogger('netkit')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

address = ('127.0.0.1', 7777)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(address)

stream = Stream(s)

box = KolaBox()
box.set_json(dict(
    endpoint='user.login',
))

stream.write(box.pack())

while True:
    # 阻塞
    buf = stream.read_with_checker(KolaBox().check)

    if buf:
        box2 = KolaBox()
        box2.unpack(buf)
        print box2

    if stream.closed():
        print 'server closed'
        break

s.close()
