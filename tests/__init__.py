#
# Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 Courgette
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import logging
from unittest import TestCase
from mock import patch
from mockito import when
from b3.config import CfgConfigParser, XmlConfigParser
from b3.fake import FakeConsole, FakeClient
from b3.plugins.admin import AdminPlugin
from servermonitor import ServermonitorPlugin
from b3.output import VERBOSE


class ServermonitorTestCase(TestCase):
    """
    TestCase suitable for testing the ServermonitorPlugin class
    """

    def setUp(self):
        # less logging
        self.logger = logging.getLogger('output')
        self.logger.setLevel(logging.ERROR)
        self.logger.propagate = False


        # create a Fake parser
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString("""<configuration><settings name="server"><set name="game_log"></set></settings></configuration>""")
        self.console = FakeConsole(self.parser_conf)
        self.console.startup()

        # load the admin plugin
        self.adminPlugin = AdminPlugin(self.console, '@b3/conf/plugin_admin.xml')
        self.adminPlugin._commands = {} # work around known bug in the Admin plugin which makes the _command property shared between all instances
        self.adminPlugin.onStartup()

        # make sure the admin plugin obtained by other plugins is our admin plugin
        when(self.console).getPlugin('admin').thenReturn(self.adminPlugin)

        # load our plugin
        self.conf = CfgConfigParser()
        self.p = ServermonitorPlugin(self.console, self.conf)

        self.superadmin = FakeClient(self.console, name="Superadmin", guid="Superadmin_guid", groupBits=128)

        self.logger.propagate = True


    def init_plugin(self, config_content):
        self.logger.setLevel(VERBOSE)
        self.conf.loadFromString(config_content)
        self.p.onLoadConfig()
        self.p.onStartup()
