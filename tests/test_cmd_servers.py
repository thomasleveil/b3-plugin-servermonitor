from mockito import when, unstub
import servermonitor
from tests import ServermonitorTestCase

class Test_cmd_gamemonitor_no_param(ServermonitorTestCase):

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



class Test_cmd_gamemonitor_with_param(ServermonitorTestCase):

    def setUp(self):
        ServermonitorTestCase.setUp(self)
        self.logger.propagate = False
        self.superadmin.connects("1")
        self.superadmin.clearMessageHistory()
        self.init_plugin("""\
[commands]
servers: guest
[servers]
game-monitor.com: 1.1.1.1:27960 2.2.2.2:27960
quake3 server: 3.3.3.3:27960
""")
        self.logger.propagate = True
        when(servermonitor).http_get("http://module.game-monitor.com/1.1.1.1:27960/data/server.js").thenReturn("""={"error":0,"ip":"1.1.1.1","port":27960,"player":1,"maxplayer":12,"name":"test server 1.1.1.1"}""")
        when(servermonitor).http_get("http://module.game-monitor.com/2.2.2.2:27960/data/server.js").thenReturn("""={"error":0,"ip":"2.2.2.2","port":27960,"player":2,"maxplayer":16,"name":"test server 2.2.2.2"}""")
        when(servermonitor).quake3_info("3.3.3.3:27960").thenReturn('\xff\xff\xff\xffinfoResponse\n\\sv_maxclients\\10\\clients\\3\\mapname\\ut4_casa\\hostname\\test server 3.3.3.3')

    def tearDown(self):
        ServermonitorTestCase.tearDown(self)
        unstub()


    def test_junk(self):
        # WHEN
        self.superadmin.says("!servers f00")
        # THEN
        self.assertListEqual(['invalid server index. Try !help servers'], self.superadmin.message_history)

    def test_invalid_index_0(self):
        # WHEN
        self.superadmin.says("!servers 0")
        # THEN
        self.assertListEqual(['invalid server index. Server indexes go from 1 to 3'], self.superadmin.message_history)

    def test_invalid_index_4(self):
        # WHEN
        self.superadmin.says("!servers 4")
        # THEN
        self.assertListEqual(['invalid server index. Server indexes go from 1 to 3'], self.superadmin.message_history)

    def test_nominal_1(self):
        # WHEN
        self.superadmin.says("!servers 1")
        # THEN
        self.assertListEqual(['1.1.1.1:27960 : 1/12 test server 1.1.1.1'], self.superadmin.message_history)

    def test_nominal_2(self):
        # WHEN
        self.superadmin.says("!servers 2")
        # THEN
        self.assertListEqual(['2.2.2.2:27960 : 2/16 test server 2.2.2.2'], self.superadmin.message_history)

    def test_nominal_3(self):
        # WHEN
        self.superadmin.says("!servers 3")
        # THEN
        self.assertListEqual(['3.3.3.3:27960 : ut4_casa 3/10 test server 3.3.3.3'], self.superadmin.message_history)

