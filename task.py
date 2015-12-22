#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class TaskRequest():
    def __init__(
        self, url, method = 'GET', body = '', headers = None,
        repeat = 1, loop = False):

        self.url = url
        self.method = method
        self.body = body
        self.repeat = repeat
        self.loop = loop
        self.error = None

        if headers:
            self.headers = headers
        else:
            self.headers = {}

        if 'user-agent' not in [header.lower() for header in self.headers]:
            self.add_header('User-Agent', 'Mozilla/4.0 (compatible; Pylot)')

        if 'connection' not in [header.lower() for header in self.headers]:
            self.add_header('Connection', 'close')

        if 'accept-encoding' not in [header.lower() for header in self.headers]:
            self.add_header('Accept-Encoding', 'identity') 

    def add_header(self, header_name, value):
        self.headers[header_name] = value

class DetailPageTask(TaskRequest):
    def __init__(self, url, start_time, avl_qty):
        TaskRequest.__init__(self, url, loop = True)
        self.start_time = start_time
        self.qty = avl_qty

    def verify(self, value):
        result = value.find(self.start_time) >= 0
        msg = '' if result else '未找到匹配的活动信息'
        return result, msg

class AdvanceBuyTask(TaskRequest):
    def __init__(self, url, uid, prom_id):
        self.uid = uid
        self.prom_id = prom_id
        self.result = None

        body = 'uid=%d&prom_id=%d' % (uid, prom_id)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        TaskRequest.__init__(self, url, 'POST', body, headers, 1, True)

    def verify(self, value):
        result = value.find('not started') >= 0
        msg = '' if result else '活动尚未开始，应当返回 {"error": "not started"}'
        return result, msg

class NormalBuyTask(TaskRequest):
    def __init__(self, url, uid, prom_id):
        self.uid = uid
        self.prom_id = prom_id
        self.result = None

        body = 'uid=%d&prom_id=%d' % (uid, prom_id)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        TaskRequest.__init__(self, url, 'POST', body, headers, 1, False)

    def verify(self, value):
        result = value.find('order_id') >= 0
        if not result:
            result = value.find('sold out') >= 0

        msg = '' if result else '购买失败，应当返回订单编号等信息或抢光'
        return result, msg

class NormalPayTask(TaskRequest):
    def __init__(self, url, uid, order_id):
        self.uid = uid
        self.order_id = order_id
        self.result = None

        body = 'uid=%d&order_id=%s' % (uid, order_id)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        TaskRequest.__init__(self, url, 'POST', body, headers, 1, False)

    def verify(self, value):
        result = value.find('order_id') >= 0
        if not result:
            result = value.find('close_time') >= 0
            if not result:
                result = value.find('already paid') >= 0

        msg = '' if result else '支付失败，应当返回订单支付信息、支付超时、已经支付等'
        return result, msg

class RemainPageTask(TaskRequest):
    def __init__(self, url, avl_qty):
        TaskRequest.__init__(self, url, loop = True)
        self.qty = avl_qty

    def verify(self, value):
        prom = json.loads(value)
        result = str(prom['avl_qty']) == str(self.qty)
        msg = '' if result else '剩余可抢数量错误，正确应为 %d' % self.qty

        return result, msg

