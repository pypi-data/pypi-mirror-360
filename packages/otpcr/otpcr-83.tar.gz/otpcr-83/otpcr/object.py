# This file is placed in the Public Domain.


"clean namespace"


class Object:

    def __contains__(self, key):
        return key in dir(self)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def items(obj):
    try:
        return obj.__dict__.items()
    except AttributeError:
        return obj.items()


def keys(obj):
    try:
        return obj.__dict__.keys()
    except AttributeError:
        return obj.keys()


def update(obj, data):
    try:
        obj.__dict__.update(vars(data))
    except TypeError:
        obj.__dict__.update(data)


def values(obj):
    return obj.__dict__.values()


def __dir__():
    return (
        'Object',
        'construct',
        'fqn',
        'items',
        'keys',
        'update',
        'values'
    )
