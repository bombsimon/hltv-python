import socketio
import json

sio = socketio.Client()

EVENT_KILL = "Kill"
EVENT_ROUND_END = "RoundEnd"


@sio.event
def connect():
    ready_data = {"listId": 2336003}

    sio.emit("readyForMatch", json.dumps(ready_data))

    print("connection established")


@sio.event
def log(data):
    log_data = json.loads(data)

    if log_data is None:
        return

    if "log" not in log_data:
        return

    logs = log_data["log"]
    logs.reverse()

    for events in logs:
        for event, event_data in events.items():
            print(event, event_data)
            print("!!!")
            if event == EVENT_KILL:
                print(
                    "{} ({}) 🔫{} {} ({}) with {}".format(
                        event_data["killerName"],
                        event_data["killerSide"],
                        "💀" if event_data["headShot"] else "",
                        event_data["victimName"],
                        event_data["victimSide"],
                        event_data["weapon"],
                    )
                )

                continue

            if event == EVENT_ROUND_END:
                print(
                    "Round over, {} wins. Current score: CT {} - T {}".format(
                        event_data["winner"],
                        event_data["counterTerroristScore"],
                        event_data["terroristScore"],
                    )
                )

                continue

            print("Uncaught event: {!s}".format(event))


@sio.event
def scoreboard(data):
    pass


@sio.event
def disconnect():
    print("disconnected from server")


sio.connect("https://scorebot-secure.hltv.org")
sio.wait()
