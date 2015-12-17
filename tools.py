#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

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
