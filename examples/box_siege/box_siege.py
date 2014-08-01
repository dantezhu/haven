# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()
import gevent

import click

from netkit.stream import Stream
from reimp import Box

import time
import socket

all_run_times = 0

calc_users_count = 0
avg_qps_sum = 0


def user_connect(user_idx, reps, url):
    global all_run_times, avg_qps_sum, calc_users_count

    host, port = url.split(':')
    address = (host, int(port))
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

    send_buf = box.pack()
    run_times = 0
    t1 = time.time()
    for it in xrange(0, reps):
        all_run_times += 1
        run_times += 1
        stream.write(send_buf)
        recv_buf = stream.read_with_checker(Box().check)
        if not recv_buf:
            click.secho('user[%s] socket closed' % user_idx, fg='red')
            break

    past_time = (time.time() - t1)
    qps = run_times / past_time
    print run_times, past_time, qps
    calc_users_count += 1
    avg_qps_sum += qps

    s.close()


@click.command()
@click.argument('concurrent', type=int)
@click.argument('reps', type=int)
@click.argument('url', default='127.0.0.1:7777')
def main(concurrent, reps, url):
    click.secho('concurrent: %s, reps: %s' % (concurrent, reps), fg='green')

    jobs = []

    for it in xrange(0, concurrent):
        job = gevent.spawn(user_connect, it, reps, url)
        jobs.append(job)

    gevent.joinall(jobs)

    qps = avg_qps_sum / calc_users_count
    click.secho('jobs over. run_times: %s, qps: %s' % (all_run_times, qps), fg='yellow')

if __name__ == '__main__':
    main()