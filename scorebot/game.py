# pylint: disable=R0903
class Player:
    """
    A player represents a player in the game. The player data is populated
    on each scoreboard event and thus updated often.
    """

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
        self.hp = hp  # pylint: disable=C0103
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
    """
    Kill is a result of an kill event where the full player class is
    attached as killer, victim, assister and flaser.
    """

    def __init__(
        self,
        event_id=None,
        killer=None,
        assister=None,
        victim=None,
        weapon=None,
        flasher=None,
        headshot=False,
    ):
        self.event_id = event_id
        self.killer = killer
        self.assister = assister
        self.victim = victim
        self.weapon = weapon
        self.flasher = flasher
        self.headshot = headshot


class Team:
    """
    Team represenst one of the two teams.
    """

    def __init__(self, team_id=0, name=None, score=0, side=None, players=None):
        self.id = team_id  # pylint: disable=C0103
        self.name = name
        self.score = score
        self.side = side
        self.players = [] if players is None else players


class Scoreboard:
    """
    Scoreboard represents the current state of the scoreboard. This includes
    all the players and all data for each players.
    """

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

    def score(self):
        """
        Return the score for each team as a dictionaray where the team name
        is the key and their score is the value. This is just a convenience
        method to be able top rint the score quickly.
        """
        return {
            self.terrorists.name: self.terrorists.score,
            self.counter_terrorists.name: self.counter_terrorists.score,
        }

    def leader(self):
        """
        Leader returns a Team instance for the team and all it's players for
        the current leading team. If the socre is equal None will be returned
        """
        if self.terrorists.score > self.counter_terrorists.score:
            return self.terrorists

        if self.counter_terrorists.score > self.terrorists.score:
            return self.counter_terrorists

        return None
