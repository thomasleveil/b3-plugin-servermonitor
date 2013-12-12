import socket
from mock import Mock
from unittest2 import TestCase
from mockito import when
import sys
from servermonitor import BF3ServerInfo
import servermonitor

class Test_BF3ServerInfo(TestCase):
    def setUp(self):
        self.console = Mock()
        self.console.error = lambda x: sys.stderr.write('ERROR: %s\n' % x)
        self.maxDiff = None

    def test_nominal(self):
        # GIVEN
        sut = BF3ServerInfo(self.console, "1.2.3.4:27960", "{address} : {map} [{gamemode}] {players}/{max_players} {name}")
        when(sut).frostbite_info().thenReturn(
            ['BigBrotherBot #1 (NL)', '0', '16', 'ConquestSmall0', 'MP_001', '0', '1', '2', '250', '250', '0', '',
             'true', 'false', 'false', '712096', '712083', '109.70.149.112:25200', '', 'true', 'EU', 'lhr', 'GB',
             'false'])
        # WHEN
        sut.update()
        # THEN
        self.assertDictContainsSubset({
            'address': '1.2.3.4:27960',
            'country': 'GB',
            'gamemode': 'Conquest',
            'map': 'Grand Bazaar',
            'max_players': '16',
            'name': 'BigBrotherBot #1 (NL)',
            'players': '0',
            'region': 'EU',
            'roundsPlayed': '0',
            'roundsTotal': '1',
        }, sut.data)
        self.assertEqual('1.2.3.4:27960 : Grand Bazaar [Conquest] 0/16 BigBrotherBot #1 (NL)', str(sut))

    def test_timeout(self):
        # GIVEN
        sut = BF3ServerInfo(self.console, "1.2.3.4:27960", "{address} : {map} {players}/{max_players} {name}")
        when(sut).frostbite_info().thenRaise(socket.timeout)
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : down', str(sut))

    def test_junk_response(self):
        # GIVEN
        sut = BF3ServerInfo(self.console, "1.2.3.4:27960", "{address} : {map} {players}/{max_players} {name}")
        when(sut).frostbite_info().thenReturn('f00')
        # WHEN
        sut.update()
        # THEN
        self.assertIsNone(sut.data)
        self.assertEqual('1.2.3.4:27960 : unknown', str(sut))
