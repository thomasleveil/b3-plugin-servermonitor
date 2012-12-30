from mock import patch, call
from mockito import when
import sys
import servermonitor
from tests import ServermonitorTestCase


class Test_events(ServermonitorTestCase):

    def setUp(self):
        ServermonitorTestCase.setUp(self)
        self.say_patcher = patch.object(self.console, "say", wraps=lambda x: sys.stdout.write("SAY: %s\n" % x))
        self.say_mock = self.say_patcher.start()

    def tearDown(self):
        ServermonitorTestCase.tearDown(self)
        self.say_patcher.stop()

    def test_map_change_no_server(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[settings]
advertise on map change: yes
advertisement format: {address} : {map} {players}/{max_players} {name}
[servers]
game-monitor.com:
""")
        # WHEN
        self.console.queueEvent(self.console.getEventID("EVT_GAME_MAP_CHANGE"))
        # THEN
        self.assertListEqual([], self.say_mock.mock_calls)


    def test_map_change_with_one_server(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[settings]
advertise on map change: yes
advertisement format: {address} : {players}/{max_players} {name}
[servers]
game-monitor.com: 1.2.3.4:27960
""")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js").thenReturn("""={"ip":"1.2.3.4","port":27960,"player":15,"maxplayer":20,"name":"test server 1.2.3.4","premium":"0","link":"http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html","error":0,"query_time":"136ms"}""")
        # WHEN
        self.console.queueEvent(self.console.getEvent("EVT_GAME_MAP_CHANGE"))
        # THEN
        self.assertListEqual([call('1.2.3.4:27960 : 15/20 test server 1.2.3.4')], self.say_mock.mock_calls)


    def test_map_change_with_one_server__no(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[settings]
advertise on map change: no
advertisement format: {address} : {players}/{max_players} {name}
[servers]
game-monitor.com: 1.2.3.4:27960
""")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js").thenReturn("""={"ip":"1.2.3.4","port":27960,"player":15,"maxplayer":20,"name":"test server 1.2.3.4","premium":"0","link":"http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html","error":0,"query_time":"136ms"}""")
        # WHEN
        self.console.queueEvent(self.console.getEvent("EVT_GAME_MAP_CHANGE"))
        # THEN
        self.assertListEqual([], self.say_mock.mock_calls)
