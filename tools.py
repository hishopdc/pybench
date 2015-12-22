#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random

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
                self.move_up(9)

            self.progress_bar.update_time(elapsed_secs)

            print self.progress_bar
            print u'\n请求总数: %d\n错误: %d\n平均响应时间(毫秒): %d\n平均吞吐量(QPS): %.2f\n当前吞吐量: %.2f\n下行流量: %.1f KB\n%s' % (
                agg_count, agg_error_count, avg_resp_time * 1000, avg_throughput, cur_throughput, total_bytes_received / 1000.0, 
                '-------------------------------------------------')
            self.refreshed_once = True

        return agg_error_count == 0

class RandomUtil:
    def __init__(self):
        self.chns = u"""
        赵钱孙李周吴郑王冯陈褚卫
        蒋沈韩杨朱秦尤许何吕施张
        孔曹严华金魏陶姜戚谢邹喻
        柏水窦章云苏潘葛奚范彭郎
        鲁韦昌马苗凤花方俞任袁柳
        酆鲍史唐费廉岑薛雷贺倪汤
        滕殷罗毕郝邬安常乐于时傅
        皮卞齐康伍余元卜顾孟平黄
        和穆萧尹姚邵湛汪祁毛禹狄
        米贝明臧计伏成戴谈宋茅庞
        熊纪舒屈项祝董梁杜阮蓝闵
        席季麻强贾路娄危江童颜郭
        梅盛林刁锺徐邱骆高夏蔡田
        樊胡凌霍虞万支柯昝管卢莫
        经房裘缪干解应宗丁宣贲邓
        郁单杭洪包诸左石崔吉钮龚
        程嵇邢滑裴陆荣翁荀羊於惠
        甄麴家封芮羿储靳汲邴糜松
        井段富巫乌焦巴弓牧隗山谷
        车侯宓蓬全郗班仰秋仲伊宫
        宁仇栾暴甘钭历戎祖武符刘
        景詹束龙叶幸司韶郜黎蓟溥
        印宿白怀蒲邰从鄂索咸籍赖
        卓蔺屠蒙池乔阳郁胥能苍双
        闻莘党翟谭贡劳逄姬申扶堵
        冉宰郦雍却璩桑桂濮牛寿通
        边扈燕冀僪浦尚农温别庄晏
        柴瞿阎充慕连茹习宦艾鱼容
        向古易慎戈廖庾终暨居衡步
        都耿满弘匡国文寇广禄阙东
        欧殳沃利蔚越夔隆师巩厍聂
        晁勾敖融冷訾辛阚那简饶空
        曾毋沙乜养鞠须丰巢关蒯相
        查后荆红游竺权逮盍益桓公
        """
        self.chns = self.chns.replace('\n', '').replace(' ', '')

    def rand_name(self):
        l = len(self.chns)
        name = ''
        for i in range(random.randint(2, 3)):
            name += self.chns[random.randint(0, l - 1)]
        return name

    def rand_mobile(self):
        prefix = ['139', '138', '133', '188', '189', '186', '151', '152', '153']
        ip = random.randint(0, len(prefix) - 1);
        return '%s%04d%04d' % (prefix[ip],
                random.randint(0, 9999),
                random.randint(0, 9999))

    def rand_address(self):
        cities = [
                '长沙', '益阳', '常德', '湘潭', '株洲', '岳阳', '永州',
                '怀化', '吉首', '衡阳', '张家界', '郴州', '邵阳', '娄底'
                ]
        ic = random.randint(0, len(cities) - 1);
        return u'%s市%d路%d号-%d室' % (cities[ic],
                random.randint(0, 9999),
                random.randint(0, 9999),
                random.randint(0, 9999))
