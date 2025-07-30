# This file is placed in the Public Domain.


"clients"


import threading


from .handler import Handler


lock = threading.RLock()


"client"


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        Fleet.add(self)

    def announce(self, txt) -> None:
        pass

    def raw(self, txt) -> None:
        raise NotImplementedError("raw")

    def say(self, channel, txt) -> None:
        self.raw(txt)


"fleet"


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
            clt = Fleet.get(evt.orig)
            for tme in sorted(evt.result):
                clt.say(evt.channel, evt.result[tme])
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


"interface"


def __dir__():
    return (
        'Client',
        'Fleet'
    )
