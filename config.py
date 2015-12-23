#!/usr/bin/env python
# -*- coding: utf-8 -*-

SQL_OPT = {
    'server': '192.168.1.118',
    'user': 'bench_user',
    'password': 'qwe123123',
    'db': 'bench'
}

TEAMS = [
    {
        'name': 'Hi云',
        'captain': '何军',
        'members': '何军、彭江雄、谢惠春',
        'slogan': '404',
        'app': 'http://192.168.1.118:18001'
    },
    {
        'name': '炮灰',
        'captain': '晏志勇',
        'members': '晏志勇、戴仁蔚、周健韬',
        'slogan': '我们不是炮灰，我们是炮灰的制造者',
        'app': 'http://192.168.1.118:18002'
    },
    {
        'name': '苍狼',
        'captain': '周新星',
        'members': '周新星、蒯伟、杨彬',
        'slogan': '众志成城，挑战自我，勇者无畏，所向披靡',
        'app': 'http://192.168.1.118:18003'
    },
    {
        'name': '左右逢猿',
        'captain': '熊仲坤',
        'members': '熊仲坤、徐干、彭俊杰',
        'slogan': '404',
        'app': 'http://192.168.1.118:18004'
    },
    {
        'name': '项能兴组',
        'captain': '项能兴',
        'members': '项能兴、王薪杰、李欢',
        'slogan': '404',
        'app': 'http://192.168.1.118:18005'
    },
    {
        'name': '龙骑士',
        'captain': '章龙',
        'members': '章龙、谭文科、邓骁',
        'slogan': '404',
        'app': 'http://192.168.1.118:18006'
    },
    {
        'name': '1024',
        'captain': '廖日龙',
        'members': '廖日龙、刘礼义、 罗周宇',
        'slogan': '404',
        'app': 'http://192.168.1.118:18007'
    },
    {
        'name': '火狼',
        'captain': '刘磊',
        'members': '刘磊 、朱宇、王梓靖',
        'slogan': '火舞春秋 狼战天下',
        'app': 'http://192.168.1.118:18008'
    },
    {
        'name': '低调小咖',
        'captain': '陈裕坚',
        'members': '陈裕坚、彭佩沅、邓登阳',
        'slogan': '404',
        'app': 'http://192.168.1.118:18009'
    },
    {
        'name': '三人行',
        'captain': '刘斐',
        'members': '刘斐、孙德玉、舒波',
        'slogan': '三人行，一定行',
        'app': 'http://192.168.1.118:18010'
    },
    {
        'name': '打虎',
        'captain': '黄芳',
        'members': '黄芳、汤国永、刘志',
        'slogan': '404',
        'app': 'http://192.168.1.118:18011'
    },
    {
        'name': '菜鸟',
        'captain': '柳锋',
        'members': '柳锋、刘继先、李泽',
        'slogan': '菜鸟，菜鸟，我不屌谁屌？',
        'app': 'http://192.168.1.118:18012'
    },
    {
        'name': '臭皮匠',
        'captain': '赵崇靖',
        'members': '赵崇靖、项目刘磊、朱玲君',
        'slogan': '三个臭皮匠赛过诸葛亮',
        'app': 'http://192.168.1.118:18013'
    }
]

PROMOTION_ID = 5
RESET_DB = True
BASE_URL = 'http://10.168.169.4:12803'

AGENTS = 1
DURATION = 60
RAMPUP = 0
INTERVAL = 0
TC_XML_FILENAME = 'testcases.xml'
OUTPUT_DIR = None
TEST_NAME = None
LOG_MSGS = False

GENERATE_RESULTS = True
SHUFFLE_TESTCASES = False
WAITFOR_AGENT_FINISH = True
SMOOTH_TP_GRAPH = 1
SOCKET_TIMEOUT = 300
COOKIES_ENABLED = True

HTTP_DEBUG = False
BLOCKING = False
GUI = False
