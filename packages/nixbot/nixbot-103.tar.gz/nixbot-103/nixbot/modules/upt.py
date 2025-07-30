# This file is placed in the Public Domain.


"uptime"


import time


from ..command import STARTTIME
from ..runtime import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
