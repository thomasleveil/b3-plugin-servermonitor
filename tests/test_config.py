# -*- encoding: utf-8 -*-
import logging
import os
from unittest2 import skipUnless
from mock import patch, call
from b3.config import CfgConfigParser
from tests import ServermonitorTestCase
from servermonitor import ServermonitorPlugin, __file__ as servermonitor__file__

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(servermonitor__file__), "conf/plugin_servermonitor.cfg")
DEFAULT_ADVERTISEMENT_FORMAT = "^7{address} ^0: ^4{map} ^5{players}^7/^5{max_players} ^4{name}"

class ConfigTestCase(ServermonitorTestCase):
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


class Test_config(ConfigTestCase):

    def test_empty(self):
        # GIVEN
        self.conf.loadFromString("""
[foo]
        """)
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([
            call("The config has no section 'settings'."),
            call("The config has no section 'settings'."),
            call("The config has no section 'servers'."),
            call("The config has no section 'servers'."),
            call("The config has no section 'servers'.")
        ], self.error_mock.mock_calls)
        self.assertListEqual([call("could not find section 'commands' in the plugin config. No command can be made available.")],
            self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: no'),
            call('advertisement_format: %s' % DEFAULT_ADVERTISEMENT_FORMAT),
            call('No server loaded from config for datasource game-monitor.com'),
            call('No server loaded from config for datasource quake3 server'),
            call('No server loaded from config for datasource BF3 server')
        ], self.info_mock.mock_calls)

    @skipUnless(os.path.isfile(DEFAULT_CONFIG_FILE), "Default config file not found at " + DEFAULT_CONFIG_FILE)
    def test_default(self):
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
        self.assertListEqual([
            call('advertise servers on map change: yes'),
            call('advertisement_format: %s' % DEFAULT_ADVERTISEMENT_FORMAT),
            call('No server loaded from config for datasource game-monitor.com'),
            call('No server loaded from config for datasource quake3 server'),
            call('No server loaded from config for datasource BF3 server')
        ], self.info_mock.mock_calls)



class Test_config_commands(ConfigTestCase):

    def test_servers(self):
        # GIVEN
        self.conf.loadFromString("""
[commands]
servers: guest
        """)
        # WHEN
        self.p.register_commands()
        # THEN
        self.assertIn('servers', self.adminPlugin._commands)
        self.assertListEqual([], self.p.servers)



class Test_config_servers(ConfigTestCase):

    def test_gamemonitor(self):
        # GIVEN
        self.conf.loadFromString("""
[servers]
game-monitor.com: 1.2.3.4:27960 4.5.6.7:27960
        """)
        # WHEN
        self.p.load_conf_servers_gamemonitor()
        # THEN
        self.assertListEqual(["GamemonitorServerInfo('1.2.3.4:27960')", "GamemonitorServerInfo('4.5.6.7:27960')"], map(repr, self.p.servers))
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call("servers loaded from config for datasource 'game-monitor.com': 1.2.3.4:27960, 4.5.6.7:27960"),
        ], self.info_mock.mock_calls)


    def test_quake3(self):
        # GIVEN
        self.conf.loadFromString("""
[servers]
quake3 server: 1.2.3.4:27960 4.5.6.7:27960
        """)
        # WHEN
        self.p.load_conf_servers_quake3()
        # THEN
        self.assertListEqual(["Quake3ServerInfo('1.2.3.4:27960')", "Quake3ServerInfo('4.5.6.7:27960')"], map(repr, self.p.servers))
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call("servers loaded from config for datasource 'quake3 server': 1.2.3.4:27960, 4.5.6.7:27960")
        ], self.info_mock.mock_calls)

    def test_BF3(self):
        # GIVEN
        self.conf.loadFromString("""
[servers]
BF3 server: 1.2.3.4:27960 4.5.6.7:27960
        """)
        # WHEN
        self.p.load_conf_servers_BF3()
        # THEN
        self.assertListEqual(["BF3ServerInfo('1.2.3.4:27960')", "BF3ServerInfo('4.5.6.7:27960')"], map(repr, self.p.servers))
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call("servers loaded from config for datasource 'BF3 server': 1.2.3.4:27960, 4.5.6.7:27960")
        ], self.info_mock.mock_calls)


class Test_load_conf_settings_advertise_on_map_change(ConfigTestCase):

    def test_yes(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertise on map change: yes
        """)
        # WHEN
        self.p.load_conf_settings_advertise_on_map_change()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertTrue(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: yes'),
        ], self.info_mock.mock_calls)


    def test_no(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertise on map change: no
        """)
        # WHEN
        self.p.load_conf_settings_advertise_on_map_change()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: no'),
        ], self.info_mock.mock_calls)


    def test_junk(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertise on map change: f00
        """)
        # WHEN
        self.p.load_conf_settings_advertise_on_map_change()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([
            call("Unexpected value for setting 'advertise on map change' in section 'settings': 'f00'. Expecting 'yes' or 'no'")
        ], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertise servers on map change: no'),
        ], self.info_mock.mock_calls)



class Test_load_conf_settings_advertisement_format(ConfigTestCase):

    def test_empty(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertisement format:
        """)
        # WHEN
        self.p.load_conf_settings_advertisement_format()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([
            call('Invalid advertisement format. Cannot be empty')
        ], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertisement_format: %s' % DEFAULT_ADVERTISEMENT_FORMAT)
        ], self.info_mock.mock_calls)


    def test_junk(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertisement format: {address} : {f00}
        """)
        # WHEN
        self.p.load_conf_settings_advertisement_format()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([
            call("Invalid advertisement format '{address} : {f00}'. Invalid keyword {f00}")
        ], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertisement_format: %s' % DEFAULT_ADVERTISEMENT_FORMAT)
        ], self.info_mock.mock_calls)

    def test_no_address(self):
        # GIVEN
        self.conf.loadFromString("""
[settings]
advertisement format: {name} : {players}
        """)
        # WHEN
        self.p.load_conf_settings_advertisement_format()
        # THEN
        self.assertListEqual([], self.p.servers)
        self.assertFalse(self.p.advertise_on_map_change)
        self.assertListEqual([
            call("Invalid advertisement format '{name} : {players}'. missing mandatory keyword {address}")
        ], self.error_mock.mock_calls)
        self.assertListEqual([], self.warning_mock.mock_calls)
        self.assertListEqual([
            call('advertisement_format: %s' % DEFAULT_ADVERTISEMENT_FORMAT)
        ], self.info_mock.mock_calls)