# This file is placed in the Public Domain.


"decoder/encoder"


import json


from .object import Object, construct


class Decoder(json.JSONDecoder):

    def decode(self, s, _w=None) -> Object:
        val = json.JSONDecoder.decode(self, s)
        if isinstance(val, dict):
            return hook(val)
        return val


class Encoder(json.JSONEncoder):

    def default(self, o) -> str:
        if isinstance(o, dict):
            return o.items()
        if issubclass(type(o), Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(*args, **kw) -> None:
    kw["cls"] = Encoder
    json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def hook(objdict) -> Object:
    obj = Object()
    construct(obj, objdict)
    return obj


def load(*args, **kw) -> Object:
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.load(*args, **kw)


def loads(*args, **kw) -> Object:
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.loads(*args, **kw)


def __dir__():
    return (
        'dump',
        'dumps',
        'hook',
        'load',
        'loads'
    )
