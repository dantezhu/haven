# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()
import gevent

import click

from netkit.stream import Stream
from reimp import Box

import time
import socket


class Siege(object):

    # 经过的时间
    elapsed_time = 0
    # 总请求，如果链接失败而没发送，不算在这里
    transactions = 0
    # 成功请求数
    successful_transactions = 0
    # 失败请求数，因为connect失败导致没发的请求也算在这里. 这3个值没有绝对的相等关系
    failed_transactions = 0

    def __init__(self, concurrent, reps, url, remote_cmd):
        self.concurrent = concurrent
        self.reps = reps
        self.url = url
        self.remote_cmd = remote_cmd

    def worker(self, worker_idx):

        host, port = self.url.split(':')
        address = (host, int(port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(address)
        except:
            # 直接把所有的错误请求都加上
            self.failed_transactions += self.reps
            click.secho('worker[%s] socket connect fail' % worker_idx, fg='red')
            return

        stream = Stream(s)
        box = Box()
        if hasattr(box, 'set_json'):
            box.set_json(dict(
                endpoint=self.remote_cmd,
            ))
        else:
            box.cmd = self.remote_cmd

        send_buf = box.pack()
        for it in xrange(0, self.reps):
            self.transactions += 1
            stream.write(send_buf)
            recv_buf = stream.read_with_checker(Box().check)
            if not recv_buf:
                click.secho('worker[%s] socket closed' % worker_idx, fg='red')
                self.failed_transactions += 1
                break
            else:
                self.successful_transactions += 1

        s.close()

    def run(self):
        jobs = []

        begin_time = time.time()

        for it in xrange(0, self.concurrent):
            job = gevent.spawn(self.worker, it)
            jobs.append(job)

        gevent.joinall(jobs)

        end_time = time.time()

        self.elapsed_time = end_time - begin_time

    @property
    def transaction_rate(self):
        """
        每秒的请求数
        """
        if self.elapsed_time != 0:
            return self.transactions / self.elapsed_time
        else:
            return 0

    @property
    def response_time(self):
        """
        平均响应时间
        """
        if self.transactions != 0:
            return self.elapsed_time / self.transactions
        else:
            return 0

    @property
    def plan_transactions(self):
        """
        计划的请求数
        :return:
        """
        return self.concurrent * self.reps

    @property
    def availability(self):
        if self.plan_transactions != 0:
            return self.successful_transactions / self.plan_transactions
        else:
            return 0


@click.command()
@click.option('--concurrent', '-c', type=int, default=10, help='CONCURRENT users, default is 10')
@click.option('--reps', '-r', type=int, default=10, help='REPS, number of times to run the test.')
@click.option('--url', '-u', default='127.0.0.1:7777', help='URL, 127.0.0.1:7777')
@click.option('--remote_cmd', '-m', default=1, type=int, help='REMOTE_CMD, 1')
def main(concurrent, reps, url, remote_cmd):
    siege = Siege(concurrent, reps, url, remote_cmd)
    siege.run()
    click.secho('done')
    click.secho('Transactions: %d hits' % siege.transactions)
    click.secho('Availability: %.02f %%' % (siege.availability * 100))
    click.secho('Elapsed time: %.02f secs' % siege.elapsed_time)
    click.secho('Response time: %.02f secs' % siege.response_time)
    click.secho('Transaction rate: %.02f trans/sec' % siege.transaction_rate)
    click.secho('Successful transactions: %d hits' % siege.successful_transactions)
    click.secho('Failed transactions: %d hits' % siege.failed_transactions)

if __name__ == '__main__':
    main()