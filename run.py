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

def team_intro(team):
    print('<=========【%s】队闪亮登场 =========>' % team['name'])
    time.sleep(0.3)
    print('队长 - %s' % team['captain'])
    time.sleep(0.3)
    print('队员 - %s' % team['members'])
    time.sleep(0.3)
    print('号号- %s' % team['slogan'])

def create_promotion_task(now, delay):
    print('\n开始设置抢购活动')

    start_time = now + timedelta(0, delay)
    end_time = start_time + timedelta(0, 5 * 60 + delay)

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

def test_rush_buy(team, duration, promotion_id, qty, start_time):
    tasks = []
    for uid in range(1, 1001):
        url = team['app'] + '/promotion/buy.ashx'
        url += "?uid=%d&prom_id=%d&rnd=%d" % (uid, promotion_id, time.time())

        tasks.append(
            NormalBuyTask(url, uid, promotion_id)
        )

    stats = {}
    errors = []

    lm = LoadManager(tasks, stats, errors)
    lm.setDaemon(True)
    lm.start()

    start_time = time.time()
    reporter = RuntimeReporter(duration, stats)

    all_responsed = False
    elapsed_secs = 0
    while (time.time() < start_time + duration):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            ids = runtime_stats.keys()
            responsed = sum([runtime_stats[id].count for id in ids])
            if responsed == id_to - id_from + 1:
                all_responsed = True

            elapsed_secs = time.time() - start_time
            if not reporter.refresh(elapsed_secs, refresh_rate):
                print('测试失败！')
                break

            if all_responsed:
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
    else:
        order_count = 0
        for t in tasks:
            if 'order_id' in t.result:
                order_count += 1

    return agg_count, agg_error_count, avg_throughput, last_error, order_count

def run_team_test(team):
    team_intro(team)

    now = datetime.now()
    delay = 20
    (prom_id, prod_id, qty, price, start_time, end_time) = create_promotion_task(now, delay)

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

    print('\n')
    el = (datetime.now() - now).total_seconds()
    while el <= (delay + 5):
        el = (datetime.now() - now).total_seconds()
        move_up(2)
        print(u'\n活动开始倒计时: %4d' % (delay + 5 - el))
        time.sleep(1)

    print('================ 活动正式开始 ================')

    print('\n\n第三步：粉丝疯狂抢购')

    order_diff = 0
    for r in range(3):
        print('\n第 %d 轮抢购' % (r + 1))

        dm = DataMan(config.SQL_OPT)
        dm.open()
        dm.remove_orders()
        dm.reset_product(PRODUCT_ID)
        dm.reset_users()
        dm.close()

        (reqs, errors, qps, last_error, order_count) = test_rush_buy(team, 30, prom_id, qty, start_time)
        order_diff = order_count - qty
        if order_diff != 0:
            break

    print('\n得分情况')
    if errors == 0:
        if order_diff == 0:
            print('未出现超卖或剩余：+15')
            score += 15
        else:
            print('出现【%s %d 件】情况，此项不能得分' % ('超卖' if order_diff > 0 else '剩余', abs(order_diff)))

        print('未检测到HTTP错误：+5')
        score += 5
    else:
        if last_error.find('活动尚未开始，应当返回 {"error": "not started"}') >= 0:
            print('未检测到HTTP错误：+5')
            score += 5

        print('\n%s' % last_error)


def move_up(times):
    for i in range(times):
        esc = chr(27)
        sys.stdout.write(esc + '[G' )
        sys.stdout.write(esc + '[A' )

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
        '-T', action = 'store_true',
        dest = 'team_mode', default = False, help = '团队测试模式'
    )

    parser.add_option(
        '-n', dest = 'team_number', default = -1, type='int', help='团队编号'
    )

    (options, args) = parser.parse_args()
    try:
        if options.reset:
            reset_db()
            print('数据初始化完成！')

        elif options.team_mode:
            if options.team_number != -1:
                team = config.TEAMS[options.team_number]
                run_team_test(team)

            else:
                for team in config.TEAMS:
                    run_team_test(team)
                    time.sleep(1)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print '\n中止任务'
        sys.exit(1)
