#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import time
from threading import Thread
from loader import LoadManager
from loader import DetailTaskRequest
from tools import *
from dataman import *
import config

class ProgressBar:
    def __init__(self, duration, min_value=0, max_value=100, total_width=40):
        self.prog_bar = '[]'
        self.duration = duration
        self.min = min_value
        self.max = max_value
        self.span = max_value - min_value
        self.width = total_width
        self.amount = 0
        self.update_amount(0)

    def update_amount(self, new_amount=0):
        if new_amount < self.min: new_amount = self.min
        if new_amount > self.max: new_amount = self.max
        self.amount = new_amount

        diff_from_min = float(self.amount - self.min)
        percent_done = (diff_from_min / float(self.span)) * 100.0
        percent_done = round(percent_done)
        percent_done = int(percent_done)

        all_full = self.width - 2
        num_hashes = (percent_done / 100.0) * all_full
        num_hashes = int(round(num_hashes))

        self.prog_bar = '[' + '#' * num_hashes + ' ' * (all_full - num_hashes) + ']'

        percent_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        percent_string = str(percent_done) + '%'

        self.prog_bar = self.prog_bar[0:percent_place] + (percent_string + self.prog_bar[percent_place + len(percent_string):])

    def update_time(self, elapsed_secs):
        self.update_amount((elapsed_secs / self.duration) * 100)
        self.prog_bar += '  %ds/%ss' % (elapsed_secs, self.duration)

    def __str__(self):
        return str(self.prog_bar)


class RuntimeReporter(object):
    def __init__(self, duration, runtime_stats):
        self.runtime_stats = runtime_stats
        self.progress_bar = ProgressBar(duration)
        self.last_count = 0
        self.refreshed_once = False

    def move_up(self, times):
        for i in range(times):
            esc = chr(27)
            sys.stdout.write(esc + '[G' )
            sys.stdout.write(esc + '[A' )

    def refresh(self, elapsed_secs, refresh_rate):
        ids = self.runtime_stats.keys()
        agg_count = sum([self.runtime_stats[id].count for id in ids])
        agg_total_latency = sum([self.runtime_stats[id].total_latency for id in ids])
        agg_error_count = sum([self.runtime_stats[id].error_count for id in ids])
        total_bytes_received = sum([self.runtime_stats[id].total_bytes for id in ids])

        if agg_count > 0 and elapsed_secs > 0:
            avg_resp_time = agg_total_latency / agg_count
            avg_throughput = float(agg_count) / elapsed_secs
            interval_count = agg_count - self.last_count
            cur_throughput = float(interval_count) / refresh_rate
            self.last_count = agg_count

            if self.refreshed_once:
                self.move_up(10)

            self.progress_bar.update_time(elapsed_secs)

            print self.progress_bar
            print u'\n请求总数: %d\n错误: %d\n平均响应时间(毫秒): %d\n平均吞吐量(QPS): %.2f\n当前吞吐量: %.2f\n下行流量: %.1f KB\n%s' % (
                agg_count, agg_error_count, avg_resp_time * 1000, avg_throughput, cur_throughput, total_bytes_received / 1000.0, 
                '\n-------------------------------------------------')
            self.refreshed_once = True


def get_users(num):
    users = []
    rnd = RandomUtil()

    for i in range(num):
        u = {
            'UserId': i + 1,
            'UserName': 'u%d' % (i + 1),
            'RealName': rnd.rand_name(),
            'CellPhone': rnd.rand_mobile(),
            'Address': rnd.rand_address()
        }

        users.append(u)

    return users

def get_products():
    products = [
        {
            'ProductId': 1,
            'ProductName': '二向箔',
            'SaleCounts': 0,
            'Stock': 100
        }
    ]

    shenqi = [
        u'东皇钟', u'轩辕剑', u'盘古斧', u'炼妖壶', u'昊天塔',
        u'伏羲琴', u'神农鼎', u'崆峒印', u'昆仑镜', u'女娲石'
    ]

    for i in range(len(shenqi)):
        products.append({
            'ProductId': i + 2,
            'ProductName': shenqi[i],
            'SaleCounts': 0,
            'Stock': 100
        })

    return products 

def get_promotions():
    promotions = [
        {
            'PromotionId': 1,
            'ProductId': 1,
            'StartTime': '2015-12-16 01:35:00',
            'EndTime': '2015-12-16 02:35:00',
            'Quantity': 5,
            'Price': 100.0
        }
    ]

    return promotions 

def main():
    reload(sys)
    sys.setdefaultencoding("utf8")

    tm_start = datetime.now()
    print('HiBench 开始评测...')
    print(tm_start.strftime('%Y-%m-%d %H:%M:%S.%f\n'))

    users = get_users(2)

    if config.RESET_DB == True:
        dm = DataMan(config.SQL_OPT)
        dm.open()
        dm.clear_all()
        dm.fill_users(users)
        dm.fill_products(get_products())
        dm.fill_promotions(get_promotions())
        dm.close()

    interval = config.INTERVAL
    rampup = config.RAMPUP
    log_msgs = config.LOG_MSGS
    runtime_stats = {}
    error_queue = []

    tasks = []
    for u in users:
        url = 'http://demo.testfx.kuaidiantong.cn/promotion/index.ashx'
        url += "?uid=%d&prom_id=%d&time=%d" % (u['UserId'], 1, time.time())

        req = DetailTaskRequest(url)
        req.loop = True
        tasks.append(req)

    lm = LoadManager(
        tasks, interval, rampup, log_msgs,
        runtime_stats, error_queue
    )

    lm.setDaemon(True)
    lm.start()

    start_time = time.time()
    duration = 60 * 60
    reporter = RuntimeReporter(duration, runtime_stats)

    while (time.time() < start_time + duration):
        refresh_rate = 1
        time.sleep(refresh_rate)

        if lm.agents_started:
            elapsed_secs = time.time() - start_time
            reporter.refresh(elapsed_secs, refresh_rate)

    lm.stop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nInterrupt'
        sys.exit(1)
