SQL_OPT = {
    'server': '139.129.17.94',
    'user': 'YFXtest',
    'password': 'yfxtest123',
    'db': 'promotions'
}

RESET_DB = True

AGENTS = 1
DURATION = 60  # secs
RAMPUP = 0  # secs
INTERVAL = 0  # millisecs
TC_XML_FILENAME = 'testcases.xml'
OUTPUT_DIR = None
TEST_NAME = None
LOG_MSGS = False

GENERATE_RESULTS = True
SHUFFLE_TESTCASES = False  # randomize order of testcases per agent
WAITFOR_AGENT_FINISH = True  # wait for last requests to complete before stopping
SMOOTH_TP_GRAPH = 1  # secs.  smooth/dampen throughput graph based on an interval
SOCKET_TIMEOUT = 300  # secs
COOKIES_ENABLED = True

HTTP_DEBUG = False  # only useful when combined with blocking mode  
BLOCKING = False  # stdout blocked until test finishes, then result is returned as XML
GUI = False
