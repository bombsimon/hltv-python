#!/usr/bin/env python
"""
This is an example on how to use the Livescore class to stream the data from
an ongoing match. The example will print each frag similar to the one in
game with the fragger, assister, flasher and victim. It will also print the
team of each player, if it was a headshot and the weapon used.
"""

import asyncio
from scorebot import Livescore

# Use a global scoreboard variable to be able to access it in any event.
scoreboard = None


def on_connect():
    """
    A simple callback to ensure we got connected.
    """
    print("connected!")


def on_scoreboard(sb):
    """
    Update the global scoreboard on each event.
    """
    global scoreboard
    scoreboard = sb


def on_kill(data):
    """
    Print a log to the killfeed for each frag.
    """
    print(
        "{}{}{} ({}) 🔫{} {} ({}) with {}".format(
            data.killer.name,
            " + {}".format(data.assister.name)
            if data.assister is not None
            else "",
            " (flashed by {})".format(data.flasher.name)
            if data.flasher is not None
            else "",
            data.killer.team.name,
            "💀" if data.headshot else "",
            data.victim.name,
            data.victim.team.name,
            data.weapon,
        )
    )


def on_round_end(data):
    """
    Print the team who one the round nad the current score each time around
    is over.
    """
    winning_team = (
        scoreboard.terrorists
        if data["winner"] == Livescore.TEAM_TERRORIST
        else scoreboard.counter_terrorists
    )

    print("\n---")
    print(
        "Round won by {}. Score is now {} {} - {} {}".format(
            winning_team.name,
            scoreboard.terrorists.name,
            scoreboard.terrorists.score,
            scoreboard.counter_terrorists.score,
            scoreboard.counter_terrorists.name,
        )
    )
    print("---\n")


async def some_other_task():
    """
    A task that simulates how you would run concurrently with the socket in the
    background.
    """
    for _ in range(10):
        print("running in background")
        await asyncio.sleep(5)


async def main():
    """
    Main function that will spawn a local async method and the socket in the
    background.
    """
    ls = Livescore()
    ls.from_url(
        "https://www.hltv.org/matches/2343889/forze-vs-hellraisers-nine-to-five-4"
    )

    ls.on(ls.EVENT_CONNECT, on_connect)
    ls.on(ls.EVENT_SCOREBOARD, on_scoreboard)
    ls.on(ls.EVENT_KILL, on_kill)
    ls.on(ls.EVENT_ROUND_END, on_round_end)

    socket = await ls.socket()

    feed = asyncio.create_task(socket.wait())
    other_task = asyncio.create_task(some_other_task())

    await feed
    await other_task


if __name__ == "__main__":
    asyncio.run(main())
