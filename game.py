class Player:
    def __init__(
        self,
        adr=0,
        alive=False,
        assists=0,
        deaths=0,
        has_defusekit=False,
        helmet=False,
        hltv_id=None,
        hp=100,
        kevlar=False,
        money=0,
        name=None,
        nick=None,
        primary_weapon=None,
        rating=0,
        score=0,
        steam_id=None,
        team=None,
    ):
        self.adr = adr
        self.alive = alive
        self.assists = assists
        self.deaths = deaths
        self.has_defusekit = has_defusekit
        self.helmet = helmet
        self.hltv_id = hltv_id
        self.hp = hp
        self.kevlar = kevlar
        self.money = money
        self.name = name
        self.nick = nick
        self.primary_weapon = primary_weapon
        self.rating = rating
        self.score = score
        self.steam_id = steam_id
        self.team = team


class Kill:
    def __init__(
        self,
        event_id=None,
        killer=None,
        assister=None,
        victim=None,
        weapon=None,
        headshot=False,
    ):
        self.event_id = event_id
        self.killer = killer
        self.assister = assister
        self.victim = victim
        self.weapon = weapon
        self.headshot = headshot


class Team:
    def __init__(self, team_id=0, name=None, score=0, side=None, players=[]):
        self.id = team_id
        self.name = name
        self.score = score
        self.side = side
        self.players = players


class Scoreboard:
    def __init__(
        self,
        map_name=None,
        bomb_planted=False,
        current_round=0,
        terrorists=None,
        counter_terrorists=None,
    ):
        self.map_name = map_name
        self.bomb_planted = bomb_planted
        self.current_round = current_round
        self.terrorists = terrorists
        self.counter_terrorists = counter_terrorists

    def leader(self):
        if self.terrorists.score > self.counter_terrorists.score:
            return self.terrorists

        return self.counter_terrorists
