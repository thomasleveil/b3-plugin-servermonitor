# coding: UTF-8
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
#
import StringIO
import gzip
import json
import re
import socket
import urllib2
from b3.plugin import Plugin
#noinspection PyUnresolvedReferences
from b3.events import EVT_GAME_MAP_CHANGE

__version__ = '1.2'
__author__  = 'Courgette'


USER_AGENT =  "B3 gamemonitor plugin/%s" % __version__


def http_get(url):
    """
    return the document served by a web server at a given url
    """
    req =  urllib2.Request(url, None)
    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Accept-encoding', 'gzip')
    opener = urllib2.build_opener()
    webFile = opener.open(req)
    result = webFile.read()
    webFile.close()
    if webFile.headers.get('content-encoding', '') == 'gzip':
        result = StringIO.StringIO(result)
        gzipper = gzip.GzipFile(fileobj=result)
        result = gzipper.read()
    return result

def quake3_info(address):
    """
    return getstatus response from a quake3 based game server.
    """
    host = (address.split(':')[0], int(address.split(':')[1]))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    sock.connect(host)
    sock.send('\377\377\377\377%s\n' % 'getinfo')
    return sock.recv(1024)


class ServerInfo(object):
    """
    ServerInfo abstract base class.
    Subclasses must implement the update method which must fill in the 'info' property.
    """

    @staticmethod
    def validate_advertisement_format(format):
        format.format(address=None, map=None, players=None, max_players=None, name=None)
        if '{address}' not in format:
            raise ValueError, "missing mandatory keyword {address}"

    def __init__(self, console, address, msg_format):
        self.console = console
        self.address = address
        self.msg_format = msg_format
        self.info = None
        self._data = None

    @property
    def data(self):
        return self._data

    def update(self):
        """
        Query some service to get up to date info about the game server
        """
        raise NotImplemented

    def __str__(self):
        if not self.info:
            return "%s : unknown" % self.address
        else:
            return self.info

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.address)


class GamemonitorServerInfo(ServerInfo):
    """
    ServerInfo subclass which reads the status of game servers querying the webservice at www.game-monitor.com.
    """

    @ServerInfo.data.setter
    def data(self, value):
        if value.startswith("="):
            try:
                json_data = json.loads(value[1:], encoding='UTF-8')
            except Exception, err:
                self.console.error("Could not decode info from game-monitor.com. %s \"\"\"%s\"\"\"" % (err.message, value))
                self._data = None
            else:
                if not "error" in json_data:
                    self.console.error("Unexpected json data from game-monitor.com. %r" % json_data)
                    self._data = None
                elif json_data.get('error') != 0:
                    self.console.error("Unexpected error from game-monitor.com. %r" % json_data)
                    self._data = None
                else:
                    self._data = json_data
                    self.console.debug("data: %r" % self._data)
        else:
            self.console.error("Unexpected info from game-monitor.com. \"\"\"%s\"\"\"" % value)
            self._data = None

    def update(self):
        self.console.info("Updating info for %r" % self)
        url = "http://module.game-monitor.com/%s/data/server.js" % self.address
        self.console.debug("Downloading json from %s" % url)
        self._data = None
        self.info = None
        try:
            raw_data = http_get(url)
        except urllib2.HTTPError, err:
            if err.code == 304:
                self.console.debug("no change since last update")
            else:
                self.console.error(err)
        except Exception, err:
            self.console.error(err)
        else:
            self.data = raw_data
            if self.data:
                self.info = self.msg_format.format(
                    address=self.address,
                    map="", # sadly no map info is provided by game-monitor.com
                    players=self.data.get("player", "?"),
                    max_players=self.data.get("maxplayer", "?"),
                    name=self.data.get("name", "?")
                )



class Quake3ServerInfo(ServerInfo):
    """
    ServerInfo subclass which is able to query directly the status of game servers based on the Quake3 engine.
    """

    @ServerInfo.data.setter
    def data(self, value):
        if value.startswith("\xff\xff\xff\xffinfoResponse\n"):
            self._data = {}
            for k, v in re.findall(r"\\([^\\]*)\\([^\\]*)", value):
                self._data[k] = v
            self.console.debug("data: %r" % self._data)
        else:
            self.console.error("Unexpected response from quake3 server %s. %r" % (self.address, value))
            self._data = None

    def update(self):
        self.console.info("Updating info for %r" % self)
        self._data = None
        self.info = None
        try:
            raw_data = quake3_info(self.address)
        except socket.timeout:
            self.info = "%s : down" % self.address
        except Exception, err:
            self.console.error(err)
        else:
            self.console.verbose(repr(raw_data))
            self.data = raw_data
            if self.data:
                self.info = self.msg_format.format(
                    address=self.address,
                    map=self.data.get("mapname", "?"),
                    players=self.data.get("clients", "?"),
                    max_players=self.data.get("sv_maxclients", "?"),
                    name=self.data.get("hostname", "?")
                )


class ServermonitorPlugin(Plugin):
    """
    B3 plugin class
    """
    DEFAULT_ADVERTISE_ON_MAP_CHANGE = False
    DEFAULT_ADVERTISEMENT_FORMAT = """^7{address} ^0: ^4{map} ^5{players}^7/^5{max_players} ^4{name}"""

    def __init__(self, console, config=None):
        self.advertise_on_map_change = ServermonitorPlugin.DEFAULT_ADVERTISE_ON_MAP_CHANGE
        self.servers = []
        self.advertisement_format = ServermonitorPlugin.DEFAULT_ADVERTISEMENT_FORMAT
        Plugin.__init__(self, console, config)

    def onLoadConfig(self):
        self.register_commands()
        self.load_conf_settings_advertise_on_map_change()
        self.load_conf_settings_advertisement_format()
        self.servers = []
        self.load_conf_servers_gamemonitor()
        self.load_conf_servers_quake3()

    def onStartup(self):
        self.registerEvent(EVT_GAME_MAP_CHANGE)


    ###############################################################################################
    #
    #    config loaders
    #
    ###############################################################################################

    def load_conf_servers_gamemonitor(self):
        servers = []
        if not self.config.has_section('servers'):
            self.error("The config has no section 'servers'.")
        elif not self.config.has_option('servers', 'game-monitor.com'):
            self.warning("The config is missing 'game-monitor.com' in section 'servers'.")
        else:
            raw_server_list = self.config.get('servers', 'game-monitor.com')
            for address in re.findall("(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]):\d+", raw_server_list):
                servers.append(GamemonitorServerInfo(self.console, address, self.advertisement_format))
        if len(servers):
            self.info('servers loaded from config for datasource game-monitor.com: ' + ', '.join([_.address for _ in servers]))
            self.servers.extend(servers)
        else:
            self.info('No server loaded from config for datasource game-monitor.com')


    def load_conf_servers_quake3(self):
        servers = []
        if not self.config.has_section('servers'):
            self.error("The config has no section 'servers'.")
        elif not self.config.has_option('servers', 'quake3 server'):
            self.warning("The config is missing 'quake3 server' in section 'servers'.")
        else:
            raw_server_list = self.config.get('servers', 'quake3 server')
            for address in re.findall("\S+:\d+", raw_server_list):
                servers.append(Quake3ServerInfo(self.console, address, self.advertisement_format))
        if len(servers):
            self.info('servers loaded from config for datasource "quake3 server": ' + ', '.join([_.address for _ in servers]))
            self.servers.extend(servers)
        else:
            self.info('No server loaded from config for datasource "quake3 server"')


    def load_conf_settings_advertise_on_map_change(self):
        self.advertise_on_map_change = ServermonitorPlugin.DEFAULT_ADVERTISE_ON_MAP_CHANGE
        if not self.config.has_section('settings'):
            self.error("The config has no section 'settings'.")
        elif not self.config.has_option('settings', 'advertise on map change'):
            self.warning("The config is missing 'advertise on map change' in section 'settings'.")
        else:
            try:
                self.advertise_on_map_change = self.config.getboolean('settings', 'advertise on map change')
            except ValueError:
                self.error("Unexpected value for setting 'advertise on map change' in section 'settings': %r. Expecting 'yes' or 'no'" % self.config.get('settings', 'advertise on map change'))
            except Exception, err:
                self.error(err)
        self.info('advertise servers on map change: %s' % ('yes' if self.advertise_on_map_change else 'no'))


    def load_conf_settings_advertisement_format(self):
        self.advertisement_format = ServermonitorPlugin.DEFAULT_ADVERTISEMENT_FORMAT
        if not self.config.has_section('settings'):
            self.error("The config has no section 'settings'.")
        elif not self.config.has_option('settings', 'advertisement format'):
            self.warning("The config is missing 'advertisement format' in section 'settings'.")
        else:
            raw_format = self.config.get('settings', 'advertisement format')
            if not raw_format:
                self.error("Invalid advertisement format. Cannot be empty")
            else:
                try:
                    ServerInfo.validate_advertisement_format(raw_format)
                except KeyError, err:
                    self.error("Invalid advertisement format %r. Invalid keyword {%s}" % (raw_format, err.message))
                except ValueError, err:
                    self.error("Invalid advertisement format %r. %s" % (raw_format, err.message))
                except Exception, err:
                    self.error("Invalid advertisement format %r. %s" % (raw_format, err.message), exc_info=err)
                else:
                    self.advertisement_format = raw_format
        self.info('advertisement_format: %s' % self.advertisement_format)



    ###############################################################################################
    #
    #    event handlers
    #
    ###############################################################################################

    def onEvent(self, event):
        if len(self.servers):
            if event.type == EVT_GAME_MAP_CHANGE and self.advertise_on_map_change:
                for server in self.servers:
                    server.update()
                    self.console.say(str(server))


    ###############################################################################################
    #
    #    commands
    #
    ###############################################################################################

    def cmd_servers(self, data, client, cmd=None):
        """\
        [server #] - advertise game servers. If a server number is given advertise that server only.
        """
        if not len(self.servers):
            cmd.sayLoudOrPM(client, "no server setup")
        else:
            if not data:
                for server in self.servers:
                    server.update()
                    cmd.sayLoudOrPM(client, str(server))
            else:
                try:
                    server_index = int(data)
                except ValueError:
                    client.message("invalid server index. Try %shelp %s" % (cmd.prefix, cmd.command))
                else:
                    if not 1 <= server_index <= len(self.servers):
                        client.message("invalid server index. Server indexes go from 1 to %s" % len(self.servers))
                    else:
                        server = self.servers[server_index - 1]
                        server.update()
                        cmd.sayLoudOrPM(client, str(server))


    ###############################################################################################
    #
    #    Other methods
    #
    ###############################################################################################

    def register_commands(self):
        # get the admin plugin
        adminPlugin = self.console.getPlugin('admin')
        if not adminPlugin:
            self.error('Could not find admin plugin')
            return

        def getCmd(cmd):
            cmd = 'cmd_%s' % cmd
            if hasattr(self, cmd):
                func = getattr(self, cmd)
                return func
            return

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(cmd)
                if func:
                    adminPlugin.registerCommand(self, cmd, level, func, alias)
        else:
            self.warning("could not find section 'commands' in the plugin config. No command can be made available.")
