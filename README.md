servermonitor plugin for Big Brother Bot
========================================

http://www.bigbrotherbot.net


Description
-----------

This plugin adds a command `!servers` which displays the status (ip:port, map, players/max, name) of different game servers of your choice.
You can choose to automatically advertise those servers on map change.

You define the servers you want advertised in the plugin config file. All game servers based on the Quake3 engine can
be advertised as well as all servers supported at http://www.game-monitor.com.



Installation
------------

- copy servermonitor.py into b3/extplugins
- copy plugin_servermonitor.cfg in the same directory as your b3.xml
- add to the plugins section of your main b3 config file:

  `<plugin name="servermonitor" config="@conf/plugin_servermonitor.cfg" />`




Configuration
-------------

The config file defines three sections :


### commands

Defines the level/group required by a player to use the commands brought by this plugin.

A command alias can be defined by adding it after the command name and a `-`.

- `servers: guest` defines that the `!servers` command can be used by any player (registered or not).
- `servers: mod` defines that the `!servers` command can be used by players of the *moderator* group or any group of higher level.
- `servers-srv: admin` defines that the `!servers` command can be used by admins or players of higher level group and defines the alias `!srv`.




### settings

##### advertise on map change

Set if you want your game servers advertised automatically at map change.

Value can be `yes` or `no`. If set to `yes` then the game servers status will be shown when the map changes.



##### advertisement format

Allows you to customize the way the game server info is advertised. Default format is : `^7{address} ^0: ^4{map} ^5{players}^7/^5{max_players} ^4{name}`

Keywords you can use in the format string are :

- `{address}`     : the server address
- `{map}`         : the current map
- `{players}`     : the current number of players
- `{max_players}` : the maximum number of players accepted on the game server
- `{name}`        : the game server name


### servers

Defines the server addresses to advertise.


##### game-monitor.com

List of <ip:port> for each game server you would like advertised, separated by a space.

The servers you want advertised have to be registered on http://game-monitor.com/. Note that you cannot advertise the
current map when using game-monitor.com as a data source.

**Example :**

    game-monitor.com: 11.22.33.44:27960 11.22.33.44:27962


##### quake3 server

List of <ip:port> for each quake3 game server you would like advertised, separated by a space.

The game servers have to be based on the Quake3 game engine will be queried directly.
Works for Call of Duty servers, Urban Terror, etc

**Example :**

    quake3 server: 11.22.33.44:27960 11.22.33.44:27962



In-game user guide
------------------

### !help servers
show a brief description of the !servers command

### !servers
show current status of each game server set in the plugin config file

### @servers
like _!servers_ but will show the game server statuses to all players. (you need to be admin)

### !servers 2
show current status of the second game server set in the plugin config file

### @servers 3
show to all players the current status of the third game server set in the plugin config file. (you need to be admin)





Support
-------

Support is only provided on www.bigbrotherbot.net forums on the following topic :
http://forum.bigbrotherbot.net/plugins-by-courgette/servers-monitor-plugin-advertise-your-game-servers/




Changelog
---------

### 1.0 - 2012-12-30
  - first release

### 1.1 - 2012-12-30
  - fix issue which server list that appears empty unles we type !reconfig

### 1.2 - 2012-12-30
  - command !servers can now accept a parameter which is the server index to advertise exclusively
  - add option 'advertisement format' in config file to allow game server advertisement message customization


