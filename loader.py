#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import copy
import httplib
import os
import json
import pickle
import Queue
import random
import re
import socket
import sys
import time
import urllib2
import urlparse
from threading import Thread
from task import *
import config

GENERATE_RESULTS = config.GENERATE_RESULTS
COOKIES_ENABLED = config.COOKIES_ENABLED
HTTP_DEBUG = config.HTTP_DEBUG
SHUFFLE_TESTCASES = config.SHUFFLE_TESTCASES
WAITFOR_AGENT_FINISH = config.WAITFOR_AGENT_FINISH
SOCKET_TIMEOUT = config.SOCKET_TIMEOUT

class TaskAgent(Thread):
    def __init__(self, id, runtime_stats, task, signal):
        Thread.__init__(self)
        self.id = id
        self.runtime_stats = runtime_stats
        self.running = True
        self.count = 0
        self.error_count = 0
        self.default_timer = time.time
        self.trace_logging = False
        self.task = task
        self.signal = signal

    def run(self):
        agent_start_time = time.strftime('%H:%M:%S', time.localtime())

        total_latency = 0
        total_connect_latency = 0
        total_bytes = 0

        while self.running:
            if self.signal['setted']:
                self.cookie_jar = cookielib.CookieJar()
                resp, content, req_start_time, req_end_time, connect_end_time = self.send(self.task)
                self.count += 1

                if resp.code != 200:
                    self.error_count += 1
                    self.task.error = resp.code
                    self.task.result = content

                elif not self.task.verify(content):
                    self.error_count += 1
                    self.task.error = -1000
                    self.task.result = '返回值未通过验证:\n' + content

                else:
                    self.task.result = content

                latency = (req_end_time - req_start_time)
                connect_latency = (connect_end_time - req_start_time)
                resp_bytes = len(content)

                total_bytes += resp_bytes
                total_latency += latency
                total_connect_latency += connect_latency

                self.runtime_stats[self.id] = StatCollection(
                    resp.code, resp.msg, latency, self.count, self.error_count,
                    total_latency, total_connect_latency, total_bytes
                )
                self.runtime_stats[self.id].agent_start_time = agent_start_time

                if self.error_count > 0:
                    break

                if not self.task.loop:
                    break
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False

    def send(self, req):
        if HTTP_DEBUG:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar), urllib2.HTTPHandler(debuglevel=1))
        elif COOKIES_ENABLED:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        else:
            opener = urllib2.build_opener()
        if req.method.upper() == 'POST':
            request = urllib2.Request(req.url, req.body, req.headers)
        else:
            request = urllib2.Request(req.url, None, req.headers)

        req_start_time = self.default_timer()
        try:
            resp = opener.open(request)
            connect_end_time = self.default_timer()
            content = resp.read()
            req_end_time = self.default_timer()
        except httplib.HTTPException, e:
            connect_end_time = self.default_timer()
            resp = ErrorResponse()
            resp.code = 0
            resp.msg = str(e)
            resp.headers = {}
            content = ''
        except urllib2.HTTPError, e:
            connect_end_time = self.default_timer()
            resp = ErrorResponse()
            resp.code = e.code
            resp.msg = httplib.responses[e.code]
            resp.headers = dict(e.info())
            content = e.read()
        except urllib2.URLError, e:
            connect_end_time = self.default_timer()
            resp = ErrorResponse()
            resp.code = 0
            resp.msg = str(e.reason)
            resp.headers = {}
            content = ''

        req_end_time = self.default_timer()

        if self.trace_logging:
            self.log_http_msgs(req, request, resp, content)


        return (resp, content, req_start_time, req_end_time, connect_end_time)


class LoadManager(Thread):
    def __init__(self, tasks, runtime_stats, error_queue, output_dir = None, test_name = None):
        Thread.__init__(self)
        socket.setdefaulttimeout(SOCKET_TIMEOUT)
        self.running = True
        self.tasks = tasks
        self.num_agents = len(tasks)
        self.runtime_stats = runtime_stats
        self.error_queue = error_queue
        self.test_name = test_name

        if output_dir and test_name:
            self.output_dir = time.strftime(output_dir + '/' + test_name + '_' + 'results_%Y.%m.%d_%H.%M.%S', time.localtime())
        elif output_dir:
            self.output_dir = time.strftime(output_dir + '/' + 'results_%Y.%m.%d_%H.%M.%S', time.localtime())
        elif test_name:
            self.output_dir = time.strftime('results/' + test_name + '_' + 'results_%Y.%m.%d_%H.%M.%S', time.localtime())
        else:
            self.output_dir = time.strftime('results/results_%Y.%m.%d_%H.%M.%S', time.localtime()) 

        for i in range(self.num_agents):
            self.runtime_stats[i] = StatCollection(0, '', 0, 0, 0, 0, 0, 0)

        self.results_queue = Queue.Queue()
        self.agent_refs = []
        self.msg_queue = []

    def run(self):
        self.running = True
        self.agents_started = False
        try:
            os.makedirs(self.output_dir, 0755)
        except OSError:
            self.output_dir = self.output_dir + time.strftime('/results_%Y.%m.%d_%H.%M.%S', time.localtime())
            try:
               os.makedirs(self.output_dir, 0755)
            except OSError:
                sys.stderr.write('ERROR: Can not create output directory\n')
                sys.exit(1)

        self.results_writer = ResultWriter(self.results_queue, self.output_dir)
        self.results_writer.setDaemon(True)
        self.results_writer.start()

        signal = {
            'setted': False
        }

        print('-------------------------------------------------')
        print('开始启动并发测试')
        for i in range(self.num_agents):
            if self.running:
                agent = TaskAgent(i, self.runtime_stats, self.tasks[i], signal)
                agent.start()
                self.agent_refs.append(agent)
                agent_started_line = u'激活虚拟用户 %d 个' % (i + 1)
                if sys.platform.startswith('win'):
                    sys.stdout.write(chr(0x08) * len(agent_started_line))
                    sys.stdout.write(agent_started_line)
                else:
                    esc = chr(27) # escape key
                    sys.stdout.write(esc + '[G' )
                    sys.stdout.write(esc + '[A' )
                    sys.stdout.write(agent_started_line + '\n')

        signal['setted'] = True

        if sys.platform.startswith('win'):
            sys.stdout.write('\n')

        print '开始测试 ...\n'
        self.agents_started = True

    def stop(self, wait = True):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()

        if wait:
            keep_running = True
            while keep_running:
                keep_running = False
                for agent in self.agent_refs:
                    if agent.isAlive():
                        keep_running = True
                        time.sleep(0.1)

        self.results_writer.stop()

class ErrorResponse():
    def __init__(self):
        self.code = 0
        self.msg = 'Connection error'
        self.headers = {}

class StatCollection():
    def __init__(self, status, reason, latency, count, error_count, total_latency, total_connect_latency, total_bytes):
        self.status = status
        self.reason = reason
        self.latency = latency
        self.count = count
        self.error_count = error_count
        self.total_latency = total_latency
        self.total_connect_latency = total_connect_latency
        self.total_bytes = total_bytes

        self.agent_start_time = None

        if count > 0:
            self.avg_latency = (total_latency / count)
            self.avg_connect_latency = (total_connect_latency / count)
        else:
            self.avg_latency = 0
            self.avg_connect_latency = 0

class ResultWriter(Thread):
    def __init__(self, results_queue, output_dir):
        Thread.__init__(self)
        self.running = True
        self.results_queue = results_queue
        self.output_dir = output_dir

    def run(self):
        fh = open('%s/agent_stats.csv' % self.output_dir, 'w')
        fh.close()

        while self.running:
            try:
                q_tuple = self.results_queue.get(False)
                f = open('%s/agent_stats.csv' % self.output_dir, 'a')
                f.write('%s,%s,%s,%s,%s,%d,%s,%d,%f,%f,%s\n' % q_tuple)  # log as csv
                f.flush()
                f.close()
            except Queue.Empty:
                time.sleep(.10)

    def stop(self):
        self.running = False


