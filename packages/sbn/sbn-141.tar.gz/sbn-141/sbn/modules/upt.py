# This file is placed in the Public Domain.


"uptime"


import time


from .. import STARTTIME
from .  import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
