# Documentation

When building this library I couldn't find any documentation at all. I had to
rely on existing implementations for similar tools, however they managed to get
the information.

* [The data stream ](#The-data-stream)
* [Connecting](#Connecting)
* [Events](#Events)
  * [Log](#Log)
    * [Kill](#Kill)
    * [Assist](#Assist)
    * [BombPlanted](#BombPlanted)
    * [BombDefused](#BombDefused)
    * [RoundStart](#RoundStart)
    * [RoundEnd](#RoundEnd)
    * [PlayerJoin](#PlayerJoin)
    * [PlayerQuit](#PlayerQuit)
    * [MapChange](#MapChange)
    * [MatchStarted](#MatchStarted)
    * [Restart](#Restart)
    * [Suicide](#Suicide)
  * [Scoreboard](#Scoreboard)

## The data stream

The HLTV Scorebot can be reach using [Socket.IO](https://socket.io) which is a
protocol on top of WebSockets. Simply put, you connect to a server and register
callbacks for events on the socket. It's possible to read and write data from
the socket and this is what HLTV does. I do not know where HLTV gets this data
from but I read a forum post that one time a user posted abot the live scoring
not workign and an HLTV emplyee responded with information that Valve/ESL denied
them the data during the event.

## Connecting

I've found two possible ways where you can connect to the Socket.IO server; one
encrypted and one unencrypted.

* [scorebot-secure.hltv.org:443](#)
* [scorebot.hltv.org:80](#)

No kind of authentication is needed.

I do now know anything about rate limiting, public access or any other kind of
limitations. One usere on the HLTV forrum told people to be careful so HLTV
dosn't ban the source of too many connections to the server(s).

When connecting, the user should emit an `readyForMatch` event with JSON data
telling the `listId` to watch.

Example:

```python
ready_data = {"listId": 2336003}

socketio.emit("readyForMatch", json.dumps(ready_data))
```

## Events

There are multiple events that might be implemented to get realtime updates from a game.

### Log

The log event is the event that happens on every game update during the match. The first time after a connection the log
will be a list of all events up til this point of the match. After that only one event at a time will be sent.

#### Kill

A player has been killed.

```json
{
  "killerName": "FNS-",
  "killerNick": "FNS",
  "killerSide": "TERRORIST",
  "victimNick": "Snakes",
  "victimName": "SnakesX",
  "victimSide": "CT",
  "weapon": "sg556",
  "headShot": true,
  "eventId": 1250360633
}
```

#### Assist

A player has made an assists. Will reference the kill event with `killEventId`.

```json
{
  "assisterName": "1voltage",
  "assisterNick": "Voltage",
  "assisterSide": "CT",
  "victimNick": "crashies",
  "victimName": "crashies",
  "victimSide": "TERRORIST",
  "killEventId": 1250292212
}
```

#### BombPlanted

The C4 bomb has been planted.

```json
{
  "playerName": "ptr",
  "playerNick": "ptr",
  "ctPlayers": 2,
  "tPlayers": 5
}
```

#### BombDefused

The C4 bomb has been defused.

```json
{
  "playerName": "grim--",
  "playerNick": "Grim"
}

```

#### RoundStart

A new round is started.

````json
{}
````

#### RoundEnd

A round is ended.

```json
{
  "counterTerroristScore": 0,
  "terroristScore": 7,
  "winner": "TERRORIST",
  "winType": "Target_Bombed"
}
```

##### Available `winType`

* `Bomb_Defused`
* `CTs_Win`
* `Target_Bombed`
* `Ts_Win`

#### PlayerJoin

A player joins the server.

```json
{
  "playerName": "Lekr0",
  "playerSide": "UNASSIGNED",
  "playerNick": "Lekr0"
}
```

#### PlayerQuit

A player leaves the server.

```json
{
  "playerName": "Lekr0",
  "playerSide": "TERRORIST",
  "playerNick": "Lekr0"
}
```

#### MapChange

The map is changed.

```json
TODO
```

#### MatchStarted

The match is started.

```json
TODO
```

#### Restart

TODO

```json
TODO
```

#### Suicide

A player committed suicide.

```json
TODO
```

### Scoreboard

On most (all?) of the events reporting information about a player the
scoreboard will be updated. The scoreboard contains information about the
current game and all players in each team, just like you can see the scoreboard
in game.

```json
{
  "TERRORIST": [
    {
      "steamId": "1:1:14578668",
      "dbId": 922,
      "name": "Snappi",
      "score": 21,
      "deaths": 11,
      "assists": 0,
      "alive": true,
      "money": 3250,
      "damagePrRound": 90.9,
      "hp": 100,
      "primaryWeapon": "ak47",
      "kevlar": true,
      "helmet": true,
      "nick": "Snappi",
      "hasDefusekit": false,
      "advancedStats": {
        "kast": 14,
        "entryKills": 0,
        "entryDeaths": 1,
        "multiKillRounds": 7,
        "oneOnXWins": 0,
        "flashAssists": 0
      }
    }
    ...
  ],
  "CT": [
    {
      "steamId": "1:0:56007113",
      "dbId": 12733,
      "name": "xsepower",
      "score": 20,
      "deaths": 12,
      "assists": 0,
      "alive": true,
      "money": 4150,
      "damagePrRound": 88.8,
      "hp": 100,
      "primaryWeapon": "ssg08",
      "kevlar": false,
      "helmet": false,
      "nick": "xsepower",
      "hasDefusekit": true,
      "advancedStats": {
        "kast": 15,
        "entryKills": 4,
        "entryDeaths": 2,
        "multiKillRounds": 5,
        "oneOnXWins": 0,
        "flashAssists": 1
      }
    }
    ...
  ],
  "ctMatchHistory": {
    "firstHalf": [
      {
        "type": "lost",
        "roundOrdinal": 1,
        "survivingPlayers": 0
      },
      ...
      {
        "type": "Terrorists_Win",
        "roundOrdinal": 15,
        "survivingPlayers": 0
      }
    ],
    "secondHalf": [
      {
        "type": "lost",
        "roundOrdinal": 16,
        "survivingPlayers": 0
      }
      ...
    ]
  },
  "terroristMatchHistory": {
    "firstHalf": [
      {
        "type": "CTs_Win",
        "roundOrdinal": 1,
        "survivingPlayers": 3
      },
      ...
      {
        "type": "lost",
        "roundOrdinal": 15,
        "survivingPlayers": 0
      }
    ],
    "secondHalf": [
      {
        "type": "Terrorists_Win",
        "roundOrdinal": 16,
        "survivingPlayers": 5
      }
      ...
    ]
  },
  "bombPlanted": false,
  "mapName": "de_mirage",
  "terroristTeamName": "Heroic",
  "ctTeamName": "forZe",
  "currentRound": 20,
  "counterTerroristScore": 8,
  "terroristScore": 11,
  "ctTeamId": 8135,
  "tTeamId": 7175,
  "frozen": false,
  "live": true,
  "ctTeamScore": 8,
  "tTeamScore": 11,
  "startingCt": 7175,
  "startingT": 8135
}
```
