# -*- encoding: utf-8 -*-
import logging
import os
from unittest2 import skipUnless
from mock import patch, call
from b3.config import CfgConfigParser
from tests import ServermonitorTestCase
from servermonitor import ServermonitorPlugin, __file__ as servermonitor__file__

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(servermonitor__file__), "conf/plugin_servermonitor.cfg")

class Test_conf(ServermonitorTestCase):
    def setUp(self):
        ServermonitorTestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = ServermonitorPlugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.INFO)

        self.info_patcher = patch.object(self.p, "info", wraps=self.p.info)
        self.info_mock = self.info_patcher.start()

        self.warning_patcher = patch.object(self.p, "warning", wraps=self.p.warning)
        self.warning_mock = self.warning_patcher.start()

        self.error_patcher = patch.object(self.p, "error", wraps=self.p.error)
        self.error_mock = self.error_patcher.start()


    def tearDown(self):
        ServermonitorTestCase.tearDown(self)
        self.info_patcher.stop()
        self.warning_patcher.stop()
        self.error_patcher.stop()


    def test_empty_config(self):
        # GIVEN
        self.conf.loadFromString("""
[foo]
        """)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([call("The config has no section 'settings'."),
                              call("The config has no section 'servers'."),
                              call("The config has no section 'servers'.")],
            self.error_mock.mock_calls)
        self.assertListEqual([call("could not find section 'commands' in the plugin config. No command can be made available.")],
            self.warning_mock.mock_calls)
        self.assertListEqual([call('advertise servers on map change: no'),
                              call('No server loaded from config for datasource game-monitor.com'),
                              call('No server loaded from config for datasource "quake3 server"')],
            self.info_mock.mock_calls)


    def test_cmd_servers(self):
        # GIVEN
        self.conf.loadFromString("""
[commands]
servers: guest
        """)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertIn('servers', self.adminPlugin._commands)
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([call("The config has no section 'settings'."),
                              call("The config has no section 'servers'."),
                              call("The config has no section 'servers'.")],
            self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([call('advertise servers on map change: no'),
                              call('No server loaded from config for datasource game-monitor.com'),
                              call('No server loaded from config for datasource "quake3 server"')],
            self.info_mock.mock_calls)


    @skipUnless(os.path.isfile(DEFAULT_CONFIG_FILE), "Default config file not found at " + DEFAULT_CONFIG_FILE)
    def test_default_config(self):
        # GIVEN
        self.conf.load(DEFAULT_CONFIG_FILE)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertIn('servers', self.adminPlugin._commands)
        self.assertListEqual([], self.p.servers)
        self.assertTrue(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([call('advertise servers on map change: yes'),
                              call('No server loaded from config for datasource game-monitor.com'),
                              call('No server loaded from config for datasource "quake3 server"')],
            self.info_mock.mock_calls)


    def test_servers_gamemonitor(self):
        # GIVEN
        self.conf.loadFromString("""
[servers]
game-monitor.com: 1.2.3.4:27960 4.5.6.7:27960
        """)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertListEqual(["GamemonitorServerInfo('1.2.3.4:27960')", "GamemonitorServerInfo('4.5.6.7:27960')"], map(repr, self.p.servers))
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([call("The config has no section 'settings'.")], self.error_mock.mock_calls)
        self.assertListEqual([
            call("could not find section 'commands' in the plugin config. No command can be made available."),
            call("The config is missing 'quake3 server' in section 'servers'.")
        ], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: no'),
            call('servers loaded from config for datasource game-monitor.com: 1.2.3.4:27960, 4.5.6.7:27960'),
            call('No server loaded from config for datasource "quake3 server"'),
        ], self.info_mock.mock_calls)


    def test_servers_quake3(self):
        # GIVEN
        self.conf.loadFromString("""
[servers]
quake3 server: 1.2.3.4:27960 4.5.6.7:27960
        """)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertListEqual(["Quake3ServerInfo('1.2.3.4:27960')", "Quake3ServerInfo('4.5.6.7:27960')"], map(repr, self.p.servers))
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([call("The config has no section 'settings'.")], self.error_mock.mock_calls)
        self.assertListEqual([
            call("could not find section 'commands' in the plugin config. No command can be made available."),
            call("The config is missing 'game-monitor.com' in section 'servers'.")
        ], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: no'),
            call('No server loaded from config for datasource game-monitor.com'),
            call('servers loaded from config for datasource "quake3 server": 1.2.3.4:27960, 4.5.6.7:27960')
        ], self.info_mock.mock_calls)