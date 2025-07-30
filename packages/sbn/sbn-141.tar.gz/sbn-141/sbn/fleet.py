# This file is placed in the Public Domain.


"list of clients"


import threading


lock = threading.RLock()


class Fleet:

    clients = {}

    @staticmethod
    def add(clt) -> None:
        Fleet.clients[repr(clt)] = clt

    @staticmethod
    def all() -> []:
        yield from Fleet.clients.values()

    @staticmethod
    def announce(txt) -> None:
        for clt in Fleet.clients.values():
            clt.announce(txt)

    @staticmethod
    def display(evt) -> None:
        with lock:
            for tme in sorted(evt.result):
                Fleet.say(evt.orig, evt.channel, evt.result[tme])
            evt.ready()

    @staticmethod
    def first() -> None:
        clt =  list(Fleet.clients.values())
        res = None
        if clt:
            res = clt[0]
        return res

    @staticmethod
    def get(orig) -> None:
        return Fleet.clients.get(orig, None)

    @staticmethod
    def say(orig, channel, txt) -> None:
        clt = Fleet.get(orig)
        if clt:
            clt.say(channel, txt)

    @staticmethod
    def wait() -> None:
        for clt in Fleet.clients.values():
            if "wait" in dir(clt):
                clt.wait()


def __dir__():
    return (
        'Fleet',
    )
