import socket
from mock import Mock
from unittest2 import TestCase
from mockito import when
import sys
from servermonitor import Quake3ServerInfo
import servermonitor

class Test_Quake3ServerInfo(TestCase):
    def setUp(self):
        self.console = Mock()
        self.console.error = lambda x: sys.stderr.write('ERROR: %s\n' % x)

    def test_nominal(self):
        # GIVEN
        sut = Quake3ServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).quake3_info("1.2.3.4:27960").thenReturn(
            '\xff\xff\xff\xffinfoResponse\n\\modversion\\4.2.009\\game\\q3ut4\\auth\\1\\pure\\1\\gametype\\4\\sv_maxcli'
            'ents\\12\\clients\\2\\mapname\\ut4_casa\\hostname\\Test server name\\protocol\\68')
        # WHEN
        sut.update()
        # THEN
        self.assertDictEqual({
            'auth': '1',
            'clients': '2',
            'game': 'q3ut4',
            'gametype': '4',
            'hostname': 'Test server name',
            'mapname': 'ut4_casa',
            'modversion': '4.2.009',
            'protocol': '68',
            'pure': '1',
            'sv_maxclients': '12'},
            sut.data)
        self.assertEqual('1.2.3.4:27960 : ut4_casa 2/12 Test server name', str(sut))

    def test_timeout(self):
        # GIVEN
        sut = Quake3ServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).quake3_info("1.2.3.4:27960").thenRaise(socket.timeout)
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : down', str(sut))

    def test_junk_response(self):
        # GIVEN
        sut = Quake3ServerInfo(self.console, "1.2.3.4:27960")
        when(servermonitor).quake3_info("1.2.3.4:27960").thenReturn('f00')
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : unknown', str(sut))

