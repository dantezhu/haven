from websocket import create_connection
from kola_box import KolaBox

ws = create_connection("ws://127.0.0.1:8000/echo")
# ws = create_connection("ws://115.28.224.64:8000/echo")
print "Sending 'Hello, World'..."
box = KolaBox()
box.set_json(dict(
    endpoint=1
))
ws.send(box.pack())
print "Sent"
print "Reeiving..."
result = ws.recv()
print "Received '%r'" % result
ws.close()
