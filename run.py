#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import time
from optparse import OptionParser
from threading import Thread
from loader import LoadManager
from tools import RuntimeReporter
from dataman import *
from task import *
import config

PRODUCT_ID = 86
PROMOTION_ID = config.PROMOTION_ID
PROMOTION_QTY = 50
PROMOTION_PRICE = 168.5
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


def do_detail_task(id_from, id_to, duration, start_time):

    interval = config.INTERVAL
    rampup = config.RAMPUP
    log_msgs = config.LOG_MSGS
    runtime_stats = {}
    error_queue = []

    tasks = []
    for i in range(id_from, id_to + 1):
        url = config.BASE_URL + '/promotion/index.ashx'
        url += "?uid=%d&prom_id=%d&time=%d" % (i, 1, time.time())

        t = NotStartTask(url)
        t.start_time = start_time
        t.loop = True
        tasks.append(t)

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
                print('测试失败！')
                break

    print('请稍等，正在停止所有虚拟用户操作...')
    lm.stop(False)

    ids = runtime_stats.keys()
    agg_count = sum([runtime_stats[id].count for id in ids])
    agg_error_count = sum([runtime_stats[id].error_count for id in ids])
    agg_total_latency = sum([runtime_stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    last_error = None
    if agg_error_count > 0:
        for t in tasks:
            if t.error:
                last_error = t.result
                break


    return agg_count, agg_error_count, avg_throughput, last_error

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

    lm.stop(True)

    ids = runtime_stats.keys()
    agg_count = sum([runtime_stats[id].count for id in ids])
    agg_error_count = sum([runtime_stats[id].error_count for id in ids])
    agg_total_latency = sum([runtime_stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    ocount = 0
    for t in tasks:
        if 'order_id' in t.result:
            ocount += 1

    print(
        '======== 测试成绩 ========\nREQS: %d\nQPS: %.2f' % (
            agg_count - agg_error_count, avg_throughput
        )
    )

    print('活动数量 %d 个, 抢购成功 %d 个' % (PROMOTION_QTY, ocount))

    overbuy = ocount - PROMOTION_QTY
    if overbuy != 0:
        print('！！！出现超卖 %d 件商品' % (overbuy))
        return False

    return True

def team_intro(team):
    print('<=========【%s】队闪亮登场 =========>' % team['name'])
    time.sleep(0.3)
    print('队长 - %s' % team['captain'])
    time.sleep(0.3)
    print('队员 - %s' % team['members'])
    time.sleep(0.3)
    print('号号- %s' % team['slogan'])

def create_promotion_task():
    print('\n开始设置抢购活动')

    advance = -2
    start_time = datetime.now() + timedelta(0, advance * 60)
    end_time = start_time + timedelta(0, (5 + advance) * 60)

    dm = DataMan(config.SQL_OPT)
    dm.open()
    dm.remove_orders()
    dm.remove_promotions()
    dm.reset_product(PRODUCT_ID)
    dm.reset_users()
    dm.create_promotion(
        PROMOTION_ID, PRODUCT_ID, PROMOTION_QTY,
        PROMOTION_PRICE, start_time, end_time
    )
    dm.close()

    print('活动ID: %d' % PROMOTION_ID)
    print('产品ID: %d' % PRODUCT_ID)
    print('数量: %d' % PROMOTION_QTY)
    print('价格: %.2f' % PROMOTION_PRICE)
    print('开始时间: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('结束时间: %s' % end_time.strftime('%Y-%m-%d %H:%M:%S'))

    return PROMOTION_ID, PRODUCT_ID, PROMOTION_QTY, PROMOTION_PRICE, start_time, end_time

def test_advance_detail(team, duration, promotion_id, qty, start_time):
    tasks = []
    for uid in range(1, 11):
        url = team['app'] + '/promotion/index.ashx'
        url += "?uid=%d&prom_id=%d&rnd=%d" % (uid, promotion_id, time.time())

        tasks.append(
            DetailPageTask(url, start_time.strftime('%Y-%m-%d %H:%M:%S'), qty)
        )

    stats = {}
    errors = []

    lm = LoadManager(tasks, stats, errors)
    lm.setDaemon(True)
    lm.start()

    start_time = time.time()
    reporter = RuntimeReporter(duration, stats)

    elapsed_secs = 0
    while (time.time() < start_time + duration):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            elapsed_secs = time.time() - start_time
            if not reporter.refresh(elapsed_secs, refresh_rate):
                print('测试失败！')
                break

    print('请稍等，正在停止所有虚拟用户操作...')
    lm.stop(True)

    ids = stats.keys()
    agg_count = sum([stats[id].count for id in ids])
    agg_error_count = sum([stats[id].error_count for id in ids])
    agg_total_latency = sum([stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    last_error = None
    if agg_error_count > 0:
        for t in tasks:
            if t.error:
                last_error = t.result
                break


    return agg_count, agg_error_count, avg_throughput, last_error

def test_advance_buy(team, duration, promotion_id, qty, start_time):
    tasks = []
    for uid in range(1, 11):
        url = team['app'] + '/promotion/buy.ashx'
        url += "?uid=%d&prom_id=%d&rnd=%d" % (uid, promotion_id, time.time())

        tasks.append(
            AdvanceBuyTask(url, uid, promotion_id)
        )

    stats = {}
    errors = []

    lm = LoadManager(tasks, stats, errors)
    lm.setDaemon(True)
    lm.start()

    start_time = time.time()
    reporter = RuntimeReporter(duration, stats)

    elapsed_secs = 0
    while (time.time() < start_time + duration):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            elapsed_secs = time.time() - start_time
            if not reporter.refresh(elapsed_secs, refresh_rate):
                print('测试失败！')
                break

    print('请稍等，正在停止所有虚拟用户操作...')
    lm.stop(True)

    ids = stats.keys()
    agg_count = sum([stats[id].count for id in ids])
    agg_error_count = sum([stats[id].error_count for id in ids])
    agg_total_latency = sum([stats[id].total_latency for id in ids])

    avg_resp_time = agg_total_latency / agg_count
    avg_throughput = float(agg_count) / elapsed_secs

    last_error = None
    if agg_error_count > 0:
        for t in tasks:
            if t.error:
                last_error = t.result
                break

    return agg_count, agg_error_count, avg_throughput, last_error

def run_team_test(team):
    team_intro(team)
    (prom_id, prod_id, qty, price, start_time, end_time) = create_promotion_task()

    score = 0

    print('\n\n第一步：活动开始前详情页被粉丝疯狂刷新')
    (reqs, errors, qps, last_error) = test_advance_detail(team, 5, prom_id, qty, start_time)

    print('\n得分情况')
    if errors == 0:
        print('所有活动信息返回正确：+5')
        print('未检测到HTTP错误：+5')
        score += 10
    else:
        if last_error.find('未找到匹配的活动信息') >= 0:
            print('未检测到HTTP错误：+5')
            score += 5

        print('\n%s' % last_error)

    print('\n\n第二步：活动开始前黑客试图恶意刷单')
    (reqs, errors, qps, last_error) = test_advance_buy(team, 5, prom_id, qty, start_time)

    print('\n得分情况')
    if errors == 0:
        print('全部返回“活动未开始”：+5')
        print('未检测到HTTP错误：+5')
        score += 10
    else:
        if last_error.find('活动尚未开始，应当返回 {"error": "not started"}') >= 0:
            print('未检测到HTTP错误：+5')
            score += 5

        print('\n%s' % last_error)


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
        '-T', action = 'store_true',
        dest = 'team_mode', default = False
    )

    parser.add_option(
        '-s', dest = 'id_from', type='int', help='起始用户ID'
    )

    parser.add_option(
        '-t', dest = 'id_to', type='int', help='截止用户ID'
    )

    parser.add_option(
        '-d', dest = 'duration', type='float', help='持续时间（分钟）'
    )

    parser.add_option(
        '-n', dest = 'team_number', type='int', help='团队编号'
    )

    (options, args) = parser.parse_args()
    try:
        if options.reset:
            reset_db()
            print('数据初始化完成！')

        elif options.team_mode:
            if options.team_number != None:
                team = config.TEAMS[options.team_number]
                run_team_test(team)

            else:
                for team in config.TEAMS:
                    run_team_test(team)
                    time.sleep(1)

        elif options.detail_task:
            start_time = datetime.now()
            end_time = start_time + timedelta(0, options.duration * 60)

            print('HiBench 设置抢购活动')
            print('活动ID: %d' % PROMOTION_ID)
            print('产品ID: %d' % PRODUCT_ID)
            print('数量: %d' % PROMOTION_QTY)
            print('价格: %.2f' % PROMOTION_PRICE)
            print('开始时间: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            print('结束时间: %s' % end_time.strftime('%Y-%m-%d %H:%M:%S'))

            # 苍狼队在这里缓存了活动的信息，但没有及时过期
            dm = DataMan(config.SQL_OPT)
            dm.open()
            dm.reset_promotion(
                PROMOTION_ID, PRODUCT_ID,
                PROMOTION_QTY, PROMOTION_PRICE,
                start_time, end_time
            )
            dm.close()

            print('\nHiBench “活动详情”加压测试...')
            (reqs, errors, qps, last_error) = do_detail_task(
                options.id_from, options.id_to, options.duration,
                start_time.strftime('%Y-%m-%d %H:%M:%S')
            )

            if errors > 0:
                print('出现错误，未通过测试！\n' + last_error)

        elif options.buy_task:
            for i in range(20):
                dm = DataMan(config.SQL_OPT)
                dm.open()
                dm.reset_promotion(
                    PROMOTION_ID, PRODUCT_ID, PROMOTION_QTY,
                    PROMOTION_PRICE, 120
                )
                dm.close()

                if not do_buy_task(options.id_from, options.id_to, options.duration):
                    break

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print '\n中止任务'
        sys.exit(1)
