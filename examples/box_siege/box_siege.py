# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()
import gevent

import click

from netkit.stream import Stream
from reimp import Box

import time
import socket

run_times = 0


def user_connect(user_idx, reps, url):
    global run_times

    host, port = url.split(':')
    address = (host, int(port))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
    except:
        click.secho('user[%s] socket connect fail' % user_idx, fg='red')
        return

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

    send_buf = box.pack()
    for it in xrange(0, reps):
        run_times += 1
        stream.write(send_buf)
        recv_buf = stream.read_with_checker(Box().check)
        if not recv_buf:
            click.secho('user[%s] socket closed' % user_idx, fg='red')
            break

    s.close()


@click.command()
@click.argument('concurrent', type=int)
@click.argument('reps', type=int)
@click.argument('url', default='127.0.0.1:7777')
def main(concurrent, reps, url):
    click.secho('concurrent: %s, reps: %s' % (concurrent, reps), fg='green')

    jobs = []

    begin_time = time.time()

    for it in xrange(0, concurrent):
        job = gevent.spawn(user_connect, it, reps, url)
        jobs.append(job)

    gevent.joinall(jobs)

    end_time = time.time()

    past_time = end_time - begin_time
    if past_time != 0:
        qps = run_times / past_time
    else:
        qps = 0

    click.secho('jobs over. run_times: %s, past_time: %s, qps: %s' % (run_times, past_time, qps), fg='yellow')

if __name__ == '__main__':
    main()