# This file is placed in the Public Domain.


"modules"


import hashlib
import importlib
import importlib.util
import inspect
import os
import sys
import threading
import typing
import types
import _thread


from ..client import Fleet
from ..object import Object, items, keys
from ..thread import later, launch


lock = threading.RLock()
path = os.path.dirname(__file__)


CHECKSUM = "6a764bd4f61042734bc07834106df1f6"
MD5      = {}
NAMES    = {}


"config"


class Default(Object):

    def __getattr__(self, key):
        return self.__dict__.get(key, "")


class Main(Default):

    debug   = False
    ignore  = ''
    init    = ""
    md5     = True
    name    = __name__.split(".", maxsplit=1)[0]
    opts    = Default()
    verbose = False
    version = 204


"commands"


class Commands:

    cmds  = {}
    md5   = {}
    names = {}

    @staticmethod
    def add(func, mod=None) -> None:
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__.split(".")[-1]

    @staticmethod
    def get(cmd) -> typing.Callable:
        func = Commands.cmds.get(cmd, None)
        if not func:
            name = Commands.names.get(cmd, None)
            if not name:
                return
            if Main.md5 and not check(name):
                return
            mod = load(name)
            if mod:
                scan(mod)
                func = Commands.cmds.get(cmd)
        return func


def command(evt) -> None:
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def inits(names) -> [types.ModuleType]:
    modz = []
    for name in sorted(spl(names)):
        try:
            mod = load(name)
            if not mod:
                continue
            if "init" in dir(mod):
                thr = launch(mod.init)
                modz.append((mod, thr))
        except Exception as ex:
            later(ex)
            _thread.interrupt_main()
    return modz


def scan(mod) -> None:
    for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in cmdz.__code__.co_varnames:
            Commands.add(cmdz, mod)


def settable():
    Commands.names.update(table())


"utilities"


def debug(*args):
    for arg in args:
        sys.stderr.write(str(arg))
        sys.stderr.write("\n")
        sys.stderr.flush()


def elapsed(seconds, short=True) -> str:
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    yeas = int(nsec/yea)
    nsec -= yeas*yea
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def parse(obj, txt=None) -> None:
    if txt is None:
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args   = []
    obj.cmd    = ""
    obj.gets   = Default()
    obj.index  = None
    obj.mod    = ""
    obj.opts   = ""
    obj.result = {}
    obj.sets   = Default()
    obj.silent = Default()
    obj.txt    = txt or ""
    obj.otxt   = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            setattr(obj.silent, key, value)
            setattr(obj.gets, key, value)
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


def spl(txt) -> str:
    try:
        result = txt.split(',')
    except (TypeError, ValueError):
        result = txt
    return [x for x in result if x]


"imports"


def check(name, md5=""):
    mname = f"{__name__}.{name}"
    if sys.modules.get(mname):
        return False
    pth = os.path.join(path, name + ".py")
    spec = importlib.util.spec_from_file_location(mname, pth)
    if not spec:
        return False
    if md5sum(pth) == (md5 or MD5.get(name, None)):
        return True
    if CHECKSUM and Main.md5:
        debug(f"{name} failed md5sum check")
    return False


def getmod(name):
    mname = f"{__name__}.{name}"
    mod = sys.modules.get(mname, None)
    if mod:
        return mod
    pth = os.path.join(path, name + ".py")
    spec = importlib.util.spec_from_file_location(mname, pth)
    if not spec:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules[mname] = mod
    return mod


def gettbl(name):
    pth = os.path.join(path, "tbl.py")
    if not os.path.exists(pth):
        debug("tbl.py is not there")
        return {}
    if CHECKSUM and (md5sum(pth) != CHECKSUM):
        debug("table checksum doesn't match")
        return {}
    try:
        mod = getmod("tbl")
    except FileNotFoundError:
        debug("tbl module not found")
        return
    return getattr(mod, name, {})


def load(name) -> types.ModuleType:
    with lock:
        if name in Main.ignore:
            return
        module = None
        mname = f"{__name__}.{name}"
        module = sys.modules.get(mname, None)
        if not module:
            pth = os.path.join(path, f"{name}.py")
            if not os.path.exists(pth):
                return None
            spec = importlib.util.spec_from_file_location(mname, pth)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[mname] = module
        if Main.debug:
            module.DEBUG = True
        return module


def md5sum(modpath):
    with open(modpath, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return str(hashlib.md5(txt).hexdigest())


def mods(names="") -> [types.ModuleType]:
    res = []
    for nme in modules():
        if names and nme not in spl(names):
            continue
        mod = load(nme)
        if not mod:
            continue
        res.append(mod)
    return res


def modules(mdir="") -> [str]:
    return sorted([
                   x[:-3] for x in os.listdir(mdir or path)
                   if x.endswith(".py") and not x.startswith("__") and
                   x[:-3] not in Main.ignore
                  ])


def table():
    md5s = gettbl("MD5")
    if md5s:
        MD5.update(md5s)
    names = gettbl("NAMES")
    if names:
        NAMES.update(names)
    return NAMES


"methods"


def edit(obj, setter, skip=False) -> None:
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def fmt(obj, args=None, skip=None, plain=False) -> str:
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str):
            txt += f'{key}="{value}" '
        else:
            txt += f'{key}={value} '
    return txt.strip()


"interface"


def __dir__():
    return modules()
