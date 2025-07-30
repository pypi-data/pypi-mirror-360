# This file is placed in the Public Domain.


"fleet"


from .. import Fleet, name
from .  import fmt


def flt(event):
    clt = list(Fleet.clients.values())
    try:
        event.reply(fmt(clt[int(event.args[0])]))
    except (KeyError, IndexError, ValueError):
        event.reply(",".join([name(x).split(".")[-1] for x in clt]))
