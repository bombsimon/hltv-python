# Documentation

When building this library I couldn't find any documentation at all. I had to rely on existing implementations for
similar tools, however they managed to get the information.

* [The data stream ](#)
* [Connecting](#)
* [Events](#)
  * [Log](#)
    * [Kill](#)
    * [Assist](#)
    * [BombPlanted](#)
    * [BombDefused](#)
    * [RoundStart](#)
    * [RoundEnd](#)
    * [PlayerJoin](#)
    * [PlayerQuit](#)
    * [MapChange](#)
    * [MatchStarted](#)
    * [Restart](#)
    * [Suicide](#)
  * [Scoreboard](#)

## The data stream

The HLTV Scorebot can be reach using [Socket.IO](https://socket.io) which is a protocol on top of WebSockets. Simply
put, you connect to a server and register callbacks for events on the socket. It's possible to read and write data from
the socket and this is what HLTV does. I do not know where HLTV gets this data from but I read a forum post that one
time a user posted abot the live scoring not workign and an HLTV emplyee responded with information that Valve/ESL
denied them the data during the event.

## Connecting

I've found two possible ways where you can connect to the Socket.IO server; one encrypted and one unencrypted.

* [scorebot-secure.hltv.org:443](#)
* [scorebot.hltv.org:80](#)

No kind of authentication is needed.

I do now know anything about rate limiting, public access or any other kind of limitations. One usere on the HLTV forrum
told people to be careful so HLTV dosn't ban the source of too many connections to the server(s).

When connecting, the user should emit an `readyForMatch` event with JSON data telling the `listId` to watch.

Example:

```python
ready_data = {"listId": 2336003}

socketio.emit("readyForMatch", json.dumps(ready_data))
socketio.emit("connected")
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

#### PlayerJoin

A player joins the server.

#### PlayerQuit

A player leaves the server.

#### MapChange

#### MatchStarted

#### Restart

#### Suicide