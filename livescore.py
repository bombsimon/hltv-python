import json
import socketio

from pprint import pprint
from time import sleep
from urllib.parse import urlparse
from game import Player, Team, Scoreboard, Kill


class Livescore:
    """
    Livescore allows a connection to the HLTV scorebot to be made. When creating
    the object a callback for the events may be passed which will then be called
    upon every event.
    """

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
        self, list_id=None, scoreboard_callback=None, event_callback=None
    ):
        self.list_id = list_id
        self.player_map = {}
        self.last_assist = {"event_id": 0, "assister": None, "victim": None}
        self.sb_callback = scoreboard_callback
        self.event_callback = event_callback

    def from_url(self, url):
        parsed = urlparse(url)
        path_parts = parsed.path.split("/")

        for part in path_parts:
            if part.isnumeric():
                self.list_id = int(part)

                return

        raise Exception("Invalid URL")

    def get_player(self, nick):
        player = self.player_map[nick]

        if player is None:
            return Player()

        return player

    def wait_for_assist(self, kill):
        # Wait for 50ms to see if there is any assist event.
        sleep(0.05)

        assister = None
        if kill.event_id == self.last_assist["event_id"]:
            assister = self.last_assist["victim"]

        kill.assister = assister

        self.event_callback(kill)

    def socket(self):
        sio = socketio.Client()

        @sio.event
        def connect():
            print("connection established")
            ready_data = {"listId": self.list_id}

            sio.emit("readyForMatch", json.dumps(ready_data))

        @sio.event
        def log(data):
            log_data = json.loads(data)
            pprint(log_data)

            if log_data is None:
                return

            if "log" not in log_data:
                print("LOG NOT IN DATA, WHAT IS THIS?")
                return

            logs = log_data["log"]
            logs.reverse()

            if self.event_callback is None:
                return

            # We skip this playback and wait for the events to come one by one.
            if len(logs) > 1:
                print("Logs longer than 1?!")
                return

            for events in logs:
                for event, event_data in events.items():
                    print("EVENT: {}".format(event))
                    pprint(event_data)

                    if event == self.EVENT_KILL:
                        print("KILL")
                        kill_event = Kill(
                            event_id=event_data["eventId"],
                            killer=self.get_player(event_data["killerName"]),
                            victim=self.get_player(event_data["victimName"]),
                            assister=None,
                            headshot=event_data["headShot"],
                            weapon=event_data["weapon"],
                        )

                        self.wait_for_assist(kill_event)
                    elif event == self.EVENT_ASSIST:
                        print("ASSIST")
                        self.last_assist = {
                            "event_id": event_data["killEventId"],
                            "assister": self.get_player(
                                event_data["assisterName"]
                            ),
                            "victim": self.get_player(
                                event_data["victimName"]
                            ),
                        }
                    elif event == self.EVENT_ROUND_START:
                        print("ROUND START")
                    elif event == self.EVENT_ROUND_END:
                        print("ROUND END")
                    elif event == self.EVENT_BOMB_PLANTED:
                        print("BOMB PLANTED")
                    elif event == self.EVENT_BOMB_DEFUSED:
                        print("BOMB DEFUSED")
                    elif event == self.EVENT_PLAYER_JOIN:
                        print("PLAYER JOINED")
                    elif event == self.EVENT_PLAYER_QUIT:
                        print("PLAYER QUIT")
                    else:
                        print("Uncaught event: {!s}".format(event))

        @sio.event
        def raw(data):
            print("RAW")
            print(data)

        @sio.event
        def time(data):
            print("TIME")
            print(data)

        @sio.event
        def clock(data):
            print("CLOCK")
            print(data)

        @sio.event
        def scoreboard(data):
            players = {
                self.TEAM_COUNTER_TERRORIST: [],
                self.TEAM_TERRORIST: [],
            }

            for team in [self.TEAM_COUNTER_TERRORIST, self.TEAM_TERRORIST]:
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
                    )

                    self.player_map[player.name] = player
                    players[team].append(player)

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

            scoreboard_data = Scoreboard(
                map_name=data["mapName"],
                bomb_planted=data["bombPlanted"],
                current_round=data["currentRound"],
                terrorists=team_terrorist,
                counter_terrorists=team_counter_terrorist,
            )

            if self.sb_callback is not None:
                self.sb_callback(scoreboard_data)

        @sio.event
        def disconnect():
            print("disconnected from server")

        # Connect to the scorebot URI.
        sio.connect("https://scorebot-secure.hltv.org")

        return sio


if __name__ == "__main__":

    def sb(data):
        pass

    def event_f(data):
        from pprint import pprint

        pprint(vars(data))

    ls = Livescore(2340833, sb, event_f)
    ls.socket().wait()
