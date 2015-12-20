#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import time
from optparse import OptionParser
from threading import Thread
from loader import LoadManager
from loader import DetailTaskRequest
from loader import BuyTaskRequest
from tools import RuntimeReporter
from dataman import *
import config

PROMOTION_QTY = 50
STOCK = 100

def reset_db(product_id, stock, qty, price):
    dm = DataMan(config.SQL_OPT)
    dm.open()

    dm.clear_all()
    dm.fill_users(100)
    dm.fill_products(100)
    dm.fill_promotions(
        product_id,
        '2015-12-16 01:35:00',
        '2015-12-16 02:35:00',
        qty,
        price
    )

    dm.close()


def do_detail_task(id_from, id_to, duration):
    tm_start = datetime.now()
    print('HiBench 开始详情加压评测...')
    print(tm_start.strftime('%Y-%m-%d %H:%M:%S.%f\n'))

    interval = config.INTERVAL
    rampup = config.RAMPUP
    log_msgs = config.LOG_MSGS
    runtime_stats = {}
    error_queue = []

    tasks = []
    for i in range(id_from, id_to + 1):
        url = config.BASE_URL + '/promotion/index.ashx'
        url += "?uid=%d&prom_id=%d&time=%d" % (i, 1, time.time())

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
    duration_s = duration * 60
    reporter = RuntimeReporter(duration_s, runtime_stats)

    elapsed_secs = 0
    while (time.time() < start_time + duration_s):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            elapsed_secs = time.time() - start_time
            if not reporter.refresh(elapsed_secs, refresh_rate):
                break

    lm.stop(False)

    ids = runtime_stats.keys()
    agg_count = sum([runtime_stats[id].count for id in ids])
    agg_error_count = sum([runtime_stats[id].error_count for id in ids])
    agg_total_latency = sum([runtime_stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    print(
        '======== 系统容量测试成绩 ========\nREQS: %d\nQPS: %.2f' % (
            agg_count - agg_error_count, avg_throughput
        )
    )

    sys.exit(0)

def do_buy_task(id_from, id_to, duration):
    tm_start = datetime.now()
    print('HiBench 开始抢购评测...')
    print(tm_start.strftime('%Y-%m-%d %H:%M:%S.%f\n'))

    interval = config.INTERVAL
    rampup = config.RAMPUP
    log_msgs = config.LOG_MSGS
    runtime_stats = {}
    error_queue = []

    tasks = []
    for i in range(id_from, id_to + 1):
        url = config.BASE_URL + '/promotion/buy.ashx'

        req = BuyTaskRequest(url, i, 1)
        tasks.append(req)

    lm = LoadManager(
        tasks, interval, rampup, log_msgs,
        runtime_stats, error_queue
    )

    lm.setDaemon(True)
    lm.start()

    start_time = time.time()
    duration_s = duration * 60
    reporter = RuntimeReporter(duration_s, runtime_stats)

    all_responsed = False
    elapsed_secs = 0
    while (time.time() < start_time + duration_s):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            ids = runtime_stats.keys()
            responsed = sum([runtime_stats[id].count for id in ids])
            if responsed == id_to - id_from + 1:
                all_responsed = True

            elapsed_secs = time.time() - start_time
            if not reporter.refresh(elapsed_secs, refresh_rate):
                break

            if all_responsed:
                break

    lm.stop(False)

    ids = runtime_stats.keys()
    agg_count = sum([runtime_stats[id].count for id in ids])
    agg_error_count = sum([runtime_stats[id].error_count for id in ids])
    agg_total_latency = sum([runtime_stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    ocount = 0
    for t in tasks:
        if t.result.find('order_id') >= 0:
            ocount += 1


    print(
        '======== 测试成绩 ========\nREQS: %d\nQPS: %.2f' % (
            agg_count - agg_error_count, avg_throughput
        )
    )
    print('活动数量 %d 个, 抢购成功 %d 个' % (PROMOTION_QTY, ocount))

    overbuy = ocount - PROMOTION_QTY
    if overbuy > 0:
        print('！！！出现超卖 %d 件商品' % (overbuy))
        return False

    return True

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf8")

    usage = '用法: %prog [选项] 参数'
    parser = OptionParser(usage)

    parser.add_option(
        '-R', '--reset', action = 'store_true',
        dest = 'reset', default = False,
        help = '重置数据库'
    )
    parser.add_option(
        '-D', action = 'store_true',
        dest = 'detail_task', default = False
    )
    parser.add_option(
        '-B', action = 'store_true',
        dest = 'buy_task', default = False
    )

    parser.add_option(
        '-s', dest = 'id_from', type='int', help='起始用户ID'
    )

    parser.add_option(
        '-t', dest = 'id_to', type='int', help='截止用户ID'
    )

    parser.add_option(
        '-d', dest = 'duration', type='int', help='持续时间（分钟）'
    )

    (options, args) = parser.parse_args()
    try:
        if options.reset:
            reset_db()
            print('数据初始化完成！')

        elif options.detail_task:
            do_detail_task(options.id_from, options.id_to, options.duration)

        elif options.buy_task:
            for i in range(20):
                dm = DataMan(config.SQL_OPT)
                dm.open()
                dm.remove_orders()
                dm.close()

                if not do_buy_task(options.id_from, options.id_to, options.duration):
                    break

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print '\n中止任务'
        sys.exit(1)
