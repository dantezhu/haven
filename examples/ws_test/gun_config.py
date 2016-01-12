proc_name = 'server'
# sync/gevent
# bind = ['0.0.0.0:8000']
bind = ['127.0.0.1:8000']
workers = 2
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
# for debug
#accesslog = '-'
#loglevel = 'debug'
