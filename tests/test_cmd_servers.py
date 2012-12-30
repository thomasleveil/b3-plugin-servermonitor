from mockito import when
import servermonitor
from tests import ServermonitorTestCase

class Test_cmd_gamemonitor(ServermonitorTestCase):

    def setUp(self):
        ServermonitorTestCase.setUp(self)
        self.logger.propagate = False
        self.superadmin.connects("1")
        self.superadmin.clearMessageHistory()
        self.logger.propagate = True

    def test_no_server(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[servers]
game-monitor.com:
""")
        # WHEN
        self.superadmin.says("!servers")
        # THEN
        self.assertListEqual(['no server setup'], self.superadmin.message_history)


    def test_gamemonitor_one_server(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[servers]
game-monitor.com: 1.2.3.4:27960
""")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js").thenReturn("""={"ip":"1.2.3.4","port":27960,"player":15,"maxplayer":20,"name":"test server 1.2.3.4","premium":"0","link":"http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html","error":0,"query_time":"136ms"}""")
        # WHEN
        self.superadmin.says("!servers")
        # THEN
        self.assertListEqual(['1.2.3.4:27960 : 15/20 test server 1.2.3.4'], self.superadmin.message_history)


    def test_gamemonitor_two_servers(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[servers]
game-monitor.com: 1.2.3.4:27960 4.3.2.1:27960
""")
        when(servermonitor).http_get("http://module.game-monitor.com/1.2.3.4:27960/data/server.js").thenReturn("""={"ip":"1.2.3.4","port":27960,"player":15,"maxplayer":20,"name":"test server 1.2.3.4","premium":"0","link":"http://www.game-monitor.com/cod4_GameServer/1.2.3.4:27960/test_server.html","error":0,"query_time":"136ms"}""")
        when(servermonitor).http_get("http://module.game-monitor.com/4.3.2.1:27960/data/server.js").thenReturn("""={"ip":"4.3.2.1","port":27960,"player":12,"maxplayer":15,"name":"test server 4.3.2.1","premium":"0","link":"http://www.game-monitor.com/cod4_GameServer/4.3.2.1:27960/test_server.html","error":0,"query_time":"136ms"}""")
        # WHEN
        self.superadmin.says("!servers")
        # THEN
        self.assertListEqual(['1.2.3.4:27960 : 15/20 test server 1.2.3.4',
                              '4.3.2.1:27960 : 12/15 test server 4.3.2.1'],
            self.superadmin.message_history)


    def test_q3a_one_server(self):
        # GIVEN
        self.init_plugin("""\
[commands]
servers: guest
[servers]
game-monitor.com:
quake3 server: 1.2.3.4:27960
""")
        when(servermonitor).quake3_info("1.2.3.4:27960").thenReturn('\xff\xff\xff\xffinfoResponse\n\\modversion\\4.2.009\\game\\q3ut4\\auth\\1\\pure\\1\\gametype\\4\\sv_maxclients\\12\\clients\\2\\mapname\\ut4_casa\\hostname\\Test server name\\protocol\\68')
        # WHEN
        self.superadmin.says("!servers")
        # THEN
        self.assertListEqual(['1.2.3.4:27960 : ut4_casa 2/12 Test server name'], self.superadmin.message_history)

