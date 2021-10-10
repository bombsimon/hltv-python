#!/usr/bin/env python
"""
This is an example on how to use the Livescore class to stream the data from
an ongoing match. The example will print each frag similar to the one in
game with the fragger, assister, flasher and victim. It will also print the
team of each player, if it was a headshot and the weapon used.
"""

import asyncio
from scorebot import Livescore


class MyKillFeed:
    """
    An example class implementing a CLI kill feed.
    """

    def __init__(self):
        self.scoreboard = None

    @classmethod
    def on_connect(cls):
        """
        A simple callback to ensure we got connected.
        """
        print("connected!")

    def on_scoreboard(self, scoreboard):
        """
        Update the scoreboard on each scoreboard event.
        """
        self.scoreboard = scoreboard

    @classmethod
    def on_kill(cls, data):
        """
        Print a log to the kill feed for each frag.
        """
        assister = (
            " + {}".format(data.assister.name)
            if data.assister is not None
            else ""
        )
        flasher = (
            " (flashed by {})".format(data.flasher.name)
            if data.flasher is not None
            else ""
        )

        print(
            "{}{}{} ({}) 🔫{} {} ({}) with {}".format(
                data.killer.name,
                assister,
                flasher,
                data.killer.team.name,
                "💀" if data.headshot else "",
                data.victim.name,
                data.victim.team.name,
                data.weapon,
            )
        )

    def on_round_end(self, data):
        """
        Print the team who one the round nad the current score each time around
        is over.
        """
        winning_team = (
            self.scoreboard.terrorists
            if data["winner"] == Livescore.TEAM_TERRORIST
            else self.scoreboard.counter_terrorists
        )

        print("\n---")
        print(
            "Round won by {}. Score is now {} {} - {} {}".format(
                winning_team.name,
                self.scoreboard.terrorists.name,
                self.scoreboard.terrorists.score,
                self.scoreboard.counter_terrorists.score,
                self.scoreboard.counter_terrorists.name,
            )
        )
        print("---\n")


async def some_other_task():
    """
    A task that simulates how you would run concurrently with the socket in the
    background.
    """
    while True:
        print("running in background")
        await asyncio.sleep(5)


async def main():
    """
    Main function that will spawn a local async method and the socket in the
    background.
    """
    kill_feed = MyKillFeed()

    live_score = Livescore()
    live_score.from_url(
        "https://www.hltv.org/matches/2351906/movistar-riders-vs-g2-iem-fall-2021-europe"
    )

    live_score.on(live_score.EVENT_CONNECT, kill_feed.on_connect)
    live_score.on(live_score.EVENT_SCOREBOARD, kill_feed.on_scoreboard)
    live_score.on(live_score.EVENT_KILL, kill_feed.on_kill)
    live_score.on(live_score.EVENT_ROUND_END, kill_feed.on_round_end)

    socket = await live_score.socket()

    await socket.start_background_task(some_other_task)
    await socket.wait()


if __name__ == "__main__":
    asyncio.run(main())
