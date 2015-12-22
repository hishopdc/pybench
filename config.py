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
        'name': '1024',
        'captain': '廖日龙',
        'members': '廖日龙、刘礼义、 罗周宇',
        'slogan': '404',
        'app': 'http://192.168.1.118:18007'
    },
    {
        'name': '苍狼',
        'captain': '周新星',
        'members': '周新星、蒯伟、杨彬',
        'slogan': '众志成城，挑战自我，勇者无畏，所向披靡',
        'app': 'http://192.168.1.118:18003'
    },
    {
        'name': '火狼',
        'captain': '刘磊',
        'members': '刘磊 、朱宇、王梓靖',
        'slogan': '火舞春秋 狼战天下',
        'app': 'http://192.168.1.118:18008'
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

