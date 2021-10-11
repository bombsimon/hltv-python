import json

from time import sleep
from urllib.parse import urlparse

import socketio

from scorebot.game import Player, Team, Scoreboard, Kill


# pylint: disable=W0613
# We want to support any kind of argument passed to _noop
async def _noop(*args, **kwargs):
    pass


class Livescore:
    """
    Livescore allows a connection to the HLTV scorebot to be made. When
    creating the object a callback for the events may be passed which will
    then be called upon every event.
    """

    EVENT_CONNECT = "Connect"
    EVENT_DISCONNECT = "Disconnect"
    EVENT_PLAYBACK = "Playback"
    EVENT_SCOREBOARD = "Scoreboard"
    EVENT_ASSIST = "Assist"
    EVENT_BOMB_DEFUSED = "BombDefused"
    EVENT_BOMB_PLANTED = "BombPlanted"
    EVENT_KILL = "Kill"
    EVENT_MAP_CHANGE = "MapChange"
    EVENT_MATCH_STARTED = "MatchStarted"
    EVENT_PLAYER_JOIN = "PlayerJoin"
    EVENT_PLAYER_QUIT = "PlayerQuit"
    EVENT_RESTART = "Restart"
    EVENT_ROUND_END = "RoundEnd"
    EVENT_ROUND_START = "RoundStart"
    EVENT_RESTART = "Restart"
    EVENT_SUICIDE = "Suicide"

    WIN_TYPE_BOMB_DEFUSED = "Bomb_Defused"
    WIN_TYPE_CTS_WIN = "CTs_Win"
    WIN_TYPE_LOST = "lost"
    WIN_TYPE_ROUND_DRAW = "Round_Draw"
    WIN_TYPE_TARGET_BOMBED = "Target_Bombed"
    WIN_TYPE_TARGET_SAVED = "Target_Saved"
    WIN_TYPE_TS_WIN = "Terrorists_Win"

    TEAM_TERRORIST = "TERRORIST"
    TEAM_COUNTER_TERRORIST = "CT"

    def __init__(
        self, list_id=None, socket_uri="https://scorebot-lb.hltv.org"
    ):
        self.list_id = list_id
        self.socket_uri = socket_uri
        self.player_map = {}
        self.last_assist = {}
        self.on_event = {
            self.EVENT_CONNECT: _noop,
            self.EVENT_DISCONNECT: _noop,
            self.EVENT_PLAYBACK: _noop,
            self.EVENT_SCOREBOARD: _noop,
            self.EVENT_ASSIST: _noop,
            self.EVENT_BOMB_DEFUSED: _noop,
            self.EVENT_BOMB_PLANTED: _noop,
            self.EVENT_KILL: _noop,
            self.EVENT_MAP_CHANGE: _noop,
            self.EVENT_MATCH_STARTED: _noop,
            self.EVENT_PLAYER_JOIN: _noop,
            self.EVENT_PLAYER_QUIT: _noop,
            self.EVENT_RESTART: _noop,
            self.EVENT_ROUND_END: _noop,
            self.EVENT_ROUND_START: _noop,
            self.EVENT_RESTART: _noop,
            self.EVENT_SUICIDE: _noop,
        }

    # pylint: disable=C0103
    # The name `on` makes sense when saying `live_score.on('some_even')
    def on(self, event=None, func=_noop):
        """
        Add a new function to an event. All events are defined as constants
        in the class and should be used to call this method. By default a
        noop method is set for all events. The signature for each methods
        may vary but if nothing else is said the raw event log will be
        passed as the only argument.
        """
        self.on_event[event] = func

    def from_url(self, url):
        """
        Set the list ID to used based on a full URL. This way you can use a
        full URL from HLTV before opening the socket. Example:
        ls = Livescore()
        ls.from_url(
          "https://www.hltv.org/matches/2340838/fnatic-vs-heretics-esl-one-road-to-rio-europe"
        )
        """
        parsed = urlparse(url)
        path_parts = parsed.path.split("/")

        for part in path_parts:
            if part.isnumeric():
                self.list_id = int(part)

                return

        raise Exception("Invalid URL")

    def get_player_by_nick(self, nick):
        """
        Return a player object based on the player nick. The list of players
        will be populated from the scoreboard on each scoreboard event.
        """
        return self.player_map.get(nick, Player())

    async def wait_for_assist(self, kill):
        """
        Wait for assist will be called before dispatching to the on-kill
        event. The method will wait for 100ms to see if an assist log is
        received for the given kill and add the player who assisted to the
        kill object.
        """
        sleep(0.1)

        if kill.event_id in self.last_assist:
            assist = self.last_assist.pop(kill.event_id)
            kill.assister = assist["assister"]

        await self.on_event[self.EVENT_KILL](kill)

    async def socket(self):
        """
        This method will return the full socket setup including all required
        event listeners for the HLTV Socket.IO.
        """
        sio = socketio.AsyncClient()

        @sio.event
        # pylint: disable=W0612
        async def connect():
            """
            Called when the socket is connected. Will emit an event to get
            data for desired match. Will dispatch an empty callback for
            EVENT_CONNECT.
            """
            ready_data = {"listId": self.list_id}
            await sio.emit("readyForMatch", json.dumps(ready_data))

            await self.on_event[self.EVENT_CONNECT]()

        @sio.event
        # pylint: disable=W0612
        async def disconnect():
            """
            Called when a proper disconnect is done. Will dispatch an empty
            callback for EVENT_DISCONNECT.
            """
            await self.on_event[self.EVENT_DISCONNECT]()

        @sio.event
        # pylint: disable=W0612
        async def log(data):
            """
            Each event on the server dispatches a log event. When connecting
            all events this far in the match will be listed. This raw event
            list will be passed to the EVENT_PLAYBACK callback method. All
            following logs will be passed one by one.

            On a kill event, an instance of a Kill class will be returned
            with proper team and player classes attached. On assist events
            the assist will be stored internally to be able to map to kill
            events. For all other events the raw event log will be dispatched.
            """
            log_data = json.loads(data)

            if log_data is None:
                raise Exception("'log_data' missing")

            if "log" not in log_data:
                raise Exception("'log' not int log_data")

            logs = log_data["log"]
            logs.reverse()

            # We skip this playback and wait for the events to come one by one.
            if len(logs) > 1:
                await self.on_event[self.EVENT_PLAYBACK](logs)
                return

            for events in logs:
                for event, event_data in events.items():
                    if event == self.EVENT_KILL:
                        kill_event = Kill(
                            event_id=event_data["eventId"],
                            killer=self.get_player_by_nick(
                                event_data["killerNick"]
                            ),
                            victim=self.get_player_by_nick(
                                event_data["victimNick"]
                            ),
                            assister=None,
                            headshot=event_data["headShot"],
                            flasher=None,
                            weapon=event_data["weapon"],
                        )

                        if "flasherNick" in event_data:
                            kill_event.flasher = self.get_player_by_nick(
                                event_data["flasherNick"]
                            )

                        await self.wait_for_assist(kill_event)
                    elif event == self.EVENT_ASSIST:
                        self.last_assist[event_data["killEventId"]] = {
                            "assister": self.get_player_by_nick(
                                event_data["assisterNick"]
                            ),
                            "victim": self.get_player_by_nick(
                                event_data["victimNick"]
                            ),
                        }

                        await self.on_event[self.EVENT_ASSIST](event_data)
                    elif event in self.on_event:
                        await self.on_event[event](event_data)
                    else:
                        print("Uncaught event: {!s}".format(event))

        @sio.event
        # pylint: disable=W0612
        async def scoreboard(data):
            """
            Every time the scoreboard is updated this event will be emitted.
            This includes when a player loses HP or has changes to their
            economy. Even though it's a bit inefficient the scoreboard class
            will be completely rewritten on each event. This includes setting
            up both teams with proper Team classes and full list of all
            players with Player classes.

            A fully populated instance of the Scoreboard class will be
            passed to the EVENT_SCOREBOARD method for each emitted event.
            """
            players = {
                self.TEAM_COUNTER_TERRORIST: [],
                self.TEAM_TERRORIST: [],
            }

            team_terrorist = Team(
                team_id=data["tTeamId"],
                name=data["terroristTeamName"],
                score=data["tTeamScore"],
                players=players[self.TEAM_TERRORIST],
            )

            team_counter_terrorist = Team(
                team_id=data["ctTeamId"],
                name=data["ctTeamName"],
                score=data["ctTeamScore"],
                players=players[self.TEAM_COUNTER_TERRORIST],
            )

            for team in [self.TEAM_COUNTER_TERRORIST, self.TEAM_TERRORIST]:
                team_object = (
                    team_counter_terrorist
                    if team == self.TEAM_COUNTER_TERRORIST
                    else team_terrorist
                )

                for player in data[team]:
                    player = Player(
                        adr=player["damagePrRound"],
                        alive=player["alive"],
                        assists=player["assists"],
                        deaths=player["deaths"],
                        has_defusekit=player["hasDefusekit"],
                        helmet=player["helmet"],
                        hltv_id=player["dbId"],
                        hp=player["hp"],
                        kevlar=player["kevlar"],
                        money=player["money"],
                        name=player["name"],
                        nick=player["nick"],
                        primary_weapon=player.get("primaryWeapon", None),
                        score=player["score"],
                        steam_id=player["steamId"],
                        team=team_object,
                    )

                    self.player_map[player.nick] = player
                    players[team].append(player)

            team_terrorist.players = players[self.TEAM_TERRORIST]
            team_counter_terrorist.players = players[
                self.TEAM_COUNTER_TERRORIST
            ]

            scoreboard_data = Scoreboard(
                map_name=data["mapName"],
                bomb_planted=data["bombPlanted"],
                current_round=data["currentRound"],
                terrorists=team_terrorist,
                counter_terrorists=team_counter_terrorist,
            )

            await self.on_event[self.EVENT_SCOREBOARD](scoreboard_data)

        # Connect to the scorebot URI.
        await sio.connect(self.socket_uri, transports="websocket")

        return sio
