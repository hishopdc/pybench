#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
import time
import json
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
    print('口号- %s' % team['slogan'])

def create_promotion_task(now, duration, delay):
    print('\n开始设置抢购活动')

    start_time = now + timedelta(0, delay)
    end_time = start_time + timedelta(0, duration)

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
    for uid in range(1, 1001):
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
    for uid in range(1, 1001):
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

def test_rush_buy(team, duration, promotion_id, uid_from, uid_to):
    tasks = []
    for uid in range(uid_from, uid_to + 1):
        url = team['app'] + '/promotion/buy.ashx'

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
            ids = stats.keys()
            responsed = sum([stats[id].count for id in ids])
            if responsed == uid_to - uid_from + 1:
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
    orders = []
    if agg_error_count > 0:
        for t in tasks:
            if t.error:
                last_error = t.result
                break
    else:
        for t in tasks:
            if 'order_id' in t.result:
                o = json.loads(t.result)
                orders.append({'uid': t.uid, 'order_id': o['order_id']})

    return agg_count, agg_error_count, avg_throughput, last_error, orders

def test_rush_pay(team, duration, orders):
    tasks = []
    for o in orders:
        url = team['app'] + '/promotion/pay.ashx'

        tasks.append(
            NormalPayTask(url, o['uid'], o['order_id'])
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
            ids = stats.keys()
            responsed = sum([stats[id].count for id in ids])
            if responsed == len(orders):
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
        paid_orders = []
        for t in tasks:
            if 'order_id' in t.result:
                o = json.loads(t.result)
                paid_orders .append({'uid': t.uid, 'order_id': o['order_id']})

    return agg_count, agg_error_count, avg_throughput, last_error, paid_orders

def test_remain_detail(team, duration, promotion_id, remain):
    tasks = []
    for uid in range(1001, 2001):
        url = team['app'] + '/promotion/index.ashx'
        url += "?uid=%d&prom_id=%d&rnd=%d" % (uid, promotion_id, time.time())

        tasks.append(
            RemainPageTask(url, remain)
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

def test_rush_late(team, duration, promotion_id, uid_from, uid_to):
    tasks = []
    for uid in range(uid_from, uid_to + 1):
        url = team['app'] + '/promotion/buy.ashx'

        tasks.append(
            RushLateTask(url, uid, promotion_id)
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
            ids = stats.keys()
            responsed = sum([stats[id].count for id in ids])
            if responsed == uid_to - uid_from + 1:
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
    orders = []
    if agg_error_count > 0:
        for t in tasks:
            if t.error:
                last_error = t.result
                break
    else:
        for t in tasks:
            if 'order_id' in t.result:
                o = json.loads(t.result)
                orders.append({'uid': t.uid, 'order_id': o['order_id']})

    return agg_count, agg_error_count, avg_throughput, last_error, orders

def update_score(sjs):
    file = '/home/xdev/ws/hibench/assets/bmb.json'
    with open(file, 'w') as f:
        jsc = json.dumps(sjs, indent = 2)
        f.write(jsc)

def run_team_test(team):
    team_intro(team)
    score = 0

    sjs = None
    file = '/home/xdev/ws/hibench/assets/bmb.json'
    with open(file, 'r') as f:
        sjs = json.loads(f.read())

    ts = None
    for s in sjs:
        if s['name'] == team['name']:
            ts = s
        else:
            s['state'] = 'stopped'

    if not ts:
        sjs.append({})
        ts = sjs[len(sjs) - 1]

    ts['name'] = team['name']
    ts['captain'] = team['captain']
    ts['members'] = team['members']
    ts['slogan'] = team['slogan']
    ts['state'] = 'testing'
    ts['scores'] = []
    scores = ts['scores']
    update_score(sjs)

    now = datetime.now()
    delay = 75
    duration = 160
    (prom_id, prod_id, qty, price, start_time, end_time) = create_promotion_task(now, duration, delay)


    print('\n\n第一步：活动开始前详情页被粉丝疯狂刷新')
    (reqs, errors, qps, last_error) = test_advance_detail(team, 30, prom_id, qty, start_time)

    print('\n得分情况')

    if errors == 0:
        print('所有活动信息返回正确：+5')
        print('未检测到HTTP错误：+5')
        s1_1 = 5
        s1_2 = 5

        score += 10
    else:
        s1_1 = 0
        s1_2 = 0
        if last_error.find('未找到匹配的活动信息') >= 0:
            print('未检测到HTTP错误：+5')
            s1_2 = 5
            score += 5

        print('\n%s' % last_error)

    si = {'title': '第一步：活动开始前详情页被粉丝疯狂刷新', 'items': []}
    si['items'].append({'key': '所有活动信息返回正确', 'value': s1_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s1_2})
    scores.append(si)
    update_score(sjs)

    print('\n\n第二步：活动开始前黑客试图恶意刷单')
    (reqs, errors, qps, last_error) = test_advance_buy(team, 30, prom_id, qty, start_time)

    print('\n得分情况')
    if errors == 0:
        print('全部返回“活动未开始”：+5')
        print('未检测到HTTP错误：+5')
        s2_1 = 5
        s2_2 = 5
        score += 10
    else:
        s2_1 = 0
        s2_2 = 0
        if last_error.find('活动尚未开始，应当返回 {"error": "not started"}') >= 0:
            print('未检测到HTTP错误：+5')
            s2_2 = 5
            score += 5

        print('\n%s' % last_error)

    si = {'title': '第二步：活动开始前黑客试图恶意刷单', 'items': []}
    si['items'].append({'key': '全部返回“活动未开始”', 'value': s2_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s2_2})
    scores.append(si)
    update_score(sjs)

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
    orders = None
    for r in range(5):
        print('\n第 %d 轮抢购' % (r + 1))

        dm = DataMan(config.SQL_OPT)
        dm.open()
        dm.remove_orders()
        dm.reset_product(PRODUCT_ID)
        dm.reset_users()
        dm.close()

        (reqs, errors, qps, last_error, orders) = test_rush_buy(team, 60, prom_id, 1, 1000)
        order_diff = len(orders) - qty
        if order_diff != 0:
            break

    print('\n得分情况')
    crashed = False
    s3_1 = 0
    s3_2 = 0
    if errors == 0:
        print('未检测到HTTP错误：+5')
        s3_2 = 5
        score += 5

        if order_diff == 0:
            print('未出现超卖或剩余：+10')
            s3_1 = 10
            score += 10
        else:
            print('出现【%s %d 件】情况，此项不能得分' % ('超卖' if order_diff > 0 else '剩余', abs(order_diff)))
            print('关键性节点错误，测试中止')
            crashed = True

    else:
        if last_error.find('购买失败，应当返回订单编号等信息或抢光') >= 0:
            print('未检测到HTTP错误：+5')
            s3_2 = 5
            score += 5

        print('\n%s' % last_error)
        print('关键性节点错误，测试中止')
        crashed = True

    si = {'title': '第三步：粉丝疯狂抢购', 'items': []}
    si['items'].append({'key': '未出现超卖或剩余', 'value': s3_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s3_2})
    scores.append(si)
    update_score(sjs)

    if crashed:
        return score

    buy_time = datetime.now()

    print('\n\n第四步：铁粉买买买，假粉反悔了')
    part = orders[0: qty / 2]
    print('\n共抢到 %d 个订单，铁粉支付 %d 个订单' % (len(orders), len(part)))
    (reqs, errors, qps, last_error, paid_orders) = test_rush_pay(team, 60, part)
    pay_diff = len(paid_orders) - len(part)

    print('\n得分情况')
    crashed = False
    s4_1 = 0
    s4_2 = 0
    if errors == 0:
        print('未检测到HTTP错误：+5')
        s4_2 = 5
        score += 5

        if pay_diff == 0:
            print('铁粉订单均正常支付：+10')
            s4_1 = 10
            score += 10
        else:
            print('出现部分未正常支付情况，此项不能得分')
            print('关键性节点错误，测试中止')
            crashed = True

    else:
        if last_error.find('支付失败，应当返回订单支付信息、支付超时、已经支付等') >= 0:
            print('未检测到HTTP错误：+5')
            s4_2 = 5
            score += 5

        print('\n%s' % last_error)
        print('关键性节点错误，测试中止')
        crashed = True

    si = {'title': '第四步：铁粉买买买，假粉反悔了', 'items': []}
    si['items'].append({'key': '铁粉订单均正常支付', 'value': s4_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s4_2})
    scores.append(si)
    update_score(sjs)

    if crashed:
        return score

    print('\n')
    el = (datetime.now() - buy_time).total_seconds()
    while el <= (60 + 5):
        el = (datetime.now() - buy_time).total_seconds()
        move_up(2)
        print(u'\n支付即将超时倒计时: %4d' % (60 + 5 - el))
        time.sleep(1)

    remain = qty - len(paid_orders)
    print('\n\n第五步：没抢到的铁粉们又等到了春天')
    (reqs, errors, qps, last_error) = test_remain_detail(team, 30, prom_id, remain)

    print('\n得分情况')
    s5_1 = 0
    s5_2 = 0
    if errors == 0:
        print('可抢数量正确：+5')
        print('未检测到HTTP错误：+5')
        s5_1 = 5
        s5_2 = 5
        score += 10
    else:
        if last_error.find('剩余可抢数量错误，正确应为') >= 0:
            print('未检测到HTTP错误：+5')
            s5_2 = 5
            score += 5

        print('\n%s' % last_error)

    si = {'title': '第五步：没抢到的铁粉们又等到了春天', 'items': []}
    si['items'].append({'key': '铁粉订单均正常支付', 'value': s5_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s5_2})
    scores.append(si)
    update_score(sjs)

    print('\n\n第六步：铁粉的最后希望')

    order_diff = 0
    orders = None
    print('\n最后一轮抢购')
    (reqs, errors, qps, last_error, orders) = test_rush_buy(team, 60, prom_id, 1001, 2000)
    order_diff = len(orders) - remain

    print('\n得分情况')
    crashed = False
    s6_1 = 0
    s6_2 = 0
    if errors == 0:
        print('未检测到HTTP错误：+5')
        s6_2 = 5
        score += 5

        if order_diff == 0:
            print('未出现超卖或剩余：+10')
            s6_1 = 10
            score += 10
        else:
            print('出现【%s %d 件】情况，此项不能得分' % ('超卖' if order_diff > 0 else '剩余', abs(order_diff)))
            print('关键性节点错误，测试中止')
            crashed = True

    else:
        if last_error.find('购买失败，应当返回订单编号等信息或抢光') >= 0:
            print('未检测到HTTP错误：+5')
            s6_2 = 5
            score += 5

        print('\n%s' % last_error)
        print('关键性节点错误，测试中止')
        crashed = True

    si = {'title': '第六步：铁粉的最后希望', 'items': []}
    si['items'].append({'key': '未出现超卖或剩余', 'value': s6_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s6_2})
    scores.append(si)
    update_score(sjs)

    if crashed:
        return score

    print('\n\n第七步：铁粉的狂欢')
    print('\n共抢到 %d 个订单，这回全部支付完' % (len(orders)))
    (reqs, errors, qps, last_error, paid_orders) = test_rush_pay(team, 60, orders)
    pay_diff = len(paid_orders) - len(orders)

    print('\n得分情况')
    crashed = False
    s7_1 = 0
    s7_2 = 0
    s7_3 = 0
    if errors == 0:
        print('未检测到HTTP错误：+5')
        s7_3 = 5
        score += 5

        if pay_diff == 0:
            print('铁粉订单均正常支付：+5')
            print('库存及销量正确：+5')
            s7_1 = 5
            s7_2 = 5
            score += 10
        else:
            print('出现部分未正常支付情况，此项不能得分')
            print('关键性节点错误，测试中止')
            crashed = True

    else:
        if last_error.find('支付失败，应当返回订单支付信息、支付超时、已经支付等') >= 0:
            print('未检测到HTTP错误：+5')
            s7_3 = 5
            score += 5

        print('\n%s' % last_error)
        print('关键性节点错误，测试中止')
        crashed = True

    si = {'title': '第七步：铁粉的狂欢', 'items': []}
    si['items'].append({'key': '铁粉订单均正常支付', 'value': s7_1})
    si['items'].append({'key': '库存及销量正确', 'value': s7_2})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s7_3})
    scores.append(si)
    update_score(sjs)

    if crashed:
        return score

    print('\n')
    el = (end_time - datetime.now()).total_seconds() + 5
    while el >= 0:
        el = (end_time - datetime.now()).total_seconds() + 5
        move_up(2)
        print(u'\n活动即将关闭倒计时: %4d' % (el))
        time.sleep(1)

    print('\n\n第八步：迟到的遗憾')
    orders = None
    (reqs, errors, qps, last_error, orders) = test_rush_late(team, 60, prom_id, 2001, 3000)

    s8_1 = 0
    s8_2 = 0
    print('\n得分情况')
    if errors == 0:
        print('全部返回正确的活动关闭或抢光状态：+5')
        print('未检测到HTTP错误：+5')
        s8_1 = 5
        s8_2 = 5
        score += 10
    else:
        if last_error.find('返回状态错误，应为活动已关闭或抢光') >= 0:
            print('未检测到HTTP错误：+5')
            s8_2 = 5
            score += 5

        print('\n%s' % last_error)


    si = {'title': '第八步：迟到的遗憾', 'items': []}
    si['items'].append({'key': '全部返回正确的活动关闭或抢光状态', 'value': s8_1})
    si['items'].append({'key': '未检测到HTTP错误', 'value': s8_2})
    scores.append(si)
    update_score(sjs)

    print('\n完成所有测试内容，开始计算总分...')
    return score

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
                score = run_team_test(team)
                print('测试结束，当前团队得分 %d' % score)

            else:
                for team in config.TEAMS:
                    score = run_team_test(team)
                    print('测试结束，当前团队得分 %d' % score)
                    time.sleep(1)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print '\n中止任务'
        sys.exit(1)
