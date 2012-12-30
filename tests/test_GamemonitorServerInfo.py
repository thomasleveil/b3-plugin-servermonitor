import socket
from mock import Mock
from unittest2 import TestCase
from mockito import when
import sys
from servermonitor import GamemonitorServerInfo
import servermonitor

class Test_GamemonitorServerInfo(TestCase):
    def setUp(self):
        self.console = Mock()
        self.console.error = lambda x: sys.stderr.write('ERROR: %s\n' % x)

    def test_nominal(self):
        # GIVEN
        sut = GamemonitorServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js")\
        .thenReturn("""={"ip":"1.2.3.4","port":27960,"player":15,"maxplayer":20,"name":"test server 1.2.3.4","premium":
        "0","link":"http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html","error":0,"query_time":
        "136ms"}""")
        # WHEN
        sut.update()
        # THEN
        self.assertDictEqual({
            u'error': 0,
            u'ip': u'1.2.3.4',
            u'link': u'http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html',
            u'maxplayer': 20,
            u'name': u'test server 1.2.3.4',
            u'player': 15,
            u'port': 27960,
            u'premium': u'0',
            u'query_time': u'136ms'},
            sut.data)
        self.assertEqual('1.2.3.4:27960 : 15/20 test server 1.2.3.4', str(sut))

    def test_timeout(self):
        # GIVEN
        sut = GamemonitorServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js")\
        .thenRaise(socket.timeout)
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : unknown', str(sut))

    def test_junk_response(self):
        # GIVEN
        sut = GamemonitorServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js")\
        .thenReturn('f00')
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : unknown', str(sut))
