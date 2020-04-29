# HLTV Livescore

This is a HLTV livescore implementation in Python. It feels super weird that I
don't find any implementations for this but I might be bad at looking. The two
JavaScript versions I found helped me understand and get inspiration.

Borrowed with pride from:

- [Nols1000/hltv-scorebot](https://github.com/Nols1000/hltv-scorebot)
- [andrewda/hltv-livescore](https://github.com/andrewda/hltv-livescore) (wraps
  above linked)
- [osebrwn/csgo-livescore](https://github.com/josebrwn/csgo-livescore) (wraps
  above linked)

Might integrate with other Python libraries in the future, such as

- [SocksPls/hltv-api](https://github.com/SocksPls/hltv-api)

## Documentation

General documentation about the Socket.IO streams can be found in
[DOCUMENTATION.md](DOCUMENTATION.md)

## Live scoring

So HLTV uses [Socket.IO](https://socket.io/) to stream the data they get from
Valve and ESL (I think?). This data is pushed on a socket. See
[DOCUMENTATION](DOCUMENTATION.md) for server information.

I actually have a really (really) hard time finding any documentation at all
regarding this socket. Is it official? Is it documented? How's it rate limited?
What events are pushed, how and when, and with what data? Because of this I've
tried to document my findings in [DOCUMENTATION.md](DOCUMENTATION.md).

## This implementation

Luckily there's a great library named
[python-socketio](https://python-socketio.readthedocs.io/en/latest/index.html)
which makes it easy for me to read from the socket. All I need to do after
connecting is to parse the stream. ✌🏼

## Usage

```python
from scorebot import Livescore

def on_kill(frag):
    print("{} killed {}".format(frag.killer.name, frag.victim.name))

ls = Livescore(123456)
ls.on(ls.EVENT_KILL, on_kill)

ls.socket().wait()
```

See [examples](examples/) folder for an implementation creating a kill feed.
