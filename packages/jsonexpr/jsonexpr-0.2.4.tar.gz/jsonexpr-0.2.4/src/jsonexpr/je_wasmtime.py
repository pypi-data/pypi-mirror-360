__copyright__ = "Copyright 2024-2025 Mark Kim"
__license__ = "Apache 2.0"
__version__ = "0.2.4"
__author__ = "Mark Kim"

import re
import os
import json
from wasmtime import Store, Module, FuncType, ValType, Linker, Engine


##############################################################################
# CONSTANTS

SCRIPTDIR     = os.path.dirname(__file__)
WASMFILE      = os.path.join(SCRIPTDIR, "je.wasm")
VERSION       = "0.2.4"
VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 4


##############################################################################
# INTERFACE

class Iface:
    def __init__(self):
        self.engine = Engine()
        self.store = Store(self.engine)
        self.linker = Linker(self.engine)

        self.linker.define_func("env", "read" , FuncType([ValType.i32(), ValType.i32(), ValType.i32()], [ValType.i32()]), self.read)
        self.linker.define_func("env", "write", FuncType([ValType.i32(), ValType.i32(), ValType.i32()], [ValType.i32()]), self.write)
        self.linker.define_func("env", "_exit", FuncType([ValType.i32()], []), self._exit)

        self.module = Module.from_file(self.engine, WASMFILE)
        self.instance = self.linker.instantiate(self.store, self.module)
        self.memory8 = self.instance.exports(self.store)["memory"].get_buffer_ptr(self.store)
        self._start = self.instance.exports(self.store)["_start"]

    def read(self, fd:"i32", buf:"i32", count:"i32") -> "i32":
        data = os.read(fd, count)
        count = len(data)

        self.memory8 = self.instance.exports(self.store)["memory"].get_buffer_ptr(self.store)
        self.memory8[buf:buf+count] = data

        return count

    def write(self, fd:"i32", buf:"i32", count:"i32") -> "i32":
        self.memory8 = self.instance.exports(self.store)["memory"].get_buffer_ptr(self.store)

        return os.write(fd, bytearray(self.memory8[buf:buf+count]))

    def _exit(self, status:"i32") -> None:
        raise Exit(status)

    def strat(self, waddr):
        count = 0

        self.memory8 = self.instance.exports(self.store)["memory"].get_buffer_ptr(self.store)

        while(self.memory8[waddr+count] != 0):
            count += 1

        return bytearray(self.memory8[waddr:waddr+count]).decode("utf-8")

    def strdup(self, string):
        encoded = string.encode("utf-8")
        waddr = self.instance.exports(self.store)["calloc"](self.store, 1, len(encoded)+1)
        self.memory8 = self.instance.exports(self.store)["memory"].get_buffer_ptr(self.store)
        self.memory8[waddr:waddr+len(string)] = encoded
        self.memory8[waddr+len(encoded)] = 0

        return waddr

    def free(self, waddr):
        self.instance.exports(self.store)["free"](self.store, waddr)

    def parse(self, wcode):
        return self.instance.exports(self.store)["parse"](self.store, wcode)

    def asteval(self, wast, wsymmap):
        return self.instance.exports(self.store)["asteval"](self.store, wast, wsymmap)

    def astfree(self, wast):
        self.instance.exports(self.store)["astfree"](self.store, wast)

    def newsym(self, wparent=0):
        return self.instance.exports(self.store)["newsym"](self.store, wparent)

    def symget(self, wsymmap, wkey):
        return self.instance.exports(self.store)["symget"](self.store, wsymmap, wkey)

    def symset(self, wsymmap, wkey, wvalue):
        return self.instance.exports(self.store)["symset"](self.store, wsymmap, wkey, wvalue, 0)

    def symfree(self, wsymmap):
        return self.instance.exports(self.store)["symfree"](self.store, wsymmap)

    def nullval(self):
        return self.instance.exports(self.store)["nullval"](self.store)

    def boolval(self, _bool):
        return self.instance.exports(self.store)["boolval"](self.store, _bool)

    def i64val(self, i64):
        return self.instance.exports(self.store)["i64val"](self.store, i64)

    def f64val(self, f64):
        return self.instance.exports(self.store)["f64val"](self.store, f64)

    def strval(self, wcstr):
        return self.instance.exports(self.store)["strval"](self.store, wcstr)

    def mapval(self):
        return self.instance.exports(self.store)["mapval"](self.store)

    def vecval(self):
        return self.instance.exports(self.store)["vecval"](self.store)

    def valdup(self, wval):
        return self.instance.exports(self.store)["valdup"](self.store, wval)

    def valtype(self, wval):
        return self.strat(self.instance.exports(self.store)["valtype"](self.store, wval))

    def valfree(self, wval):
        self.instance.exports(self.store)["valfree"](self.store, wval)

    def valtobool(self, wval):
        return self.instance.exports(self.store)["valtobool"](self.store, wval)

    def valtoi64(self, wval):
        return self.instance.exports(self.store)["valtoi64"](self.store, wval)

    def valtof64(self, wval):
        return self.instance.exports(self.store)["valtof64"](self.store, wval)

    def valtocstr(self, wval):
        return self.instance.exports(self.store)["valtocstr"](self.store, wval)

    def valtoqstr(self, wval):
        return self.instance.exports(self.store)["valtoqstr"](self.store, wval)

    def maplen(self, wmap):
        return self.instance.exports(self.store)["maplen"](self.store, wmap)

    def mapget(self, wmap, wkey):
        return self.instance.exports(self.store)["mapget"](self.store, wmap, wkey)

    def mapset(self, wmap, wkey, wval):
        return self.instance.exports(self.store)["mapset"](self.store, wmap, wkey, wval)

    def mapunset(self, wmap, wkey):
        self.instance.exports(self.store)["mapunset"](self.store, wmap, wkey)

    def mapbegin(self, wmap):
        return self.instance.exports(self.store)["mapbegin"](self.store, wmap)

    def mapend(self, wmap):
        return self.instance.exports(self.store)["mapend"](self.store, wmap)

    def mapnext(self, wmap, witer):
        return self.instance.exports(self.store)["mapnext"](self.store, wmap, witer)

    def mapgetkey(self, wmap, witer):
        return self.instance.exports(self.store)["mapgetkey"](self.store, wmap, witer)

    def mapgetval(self, wmap, witer):
        return self.instance.exports(self.store)["mapgetval"](self.store, wmap, witer)

    def veclen(self, wvec):
        return self.instance.exports(self.store)["veclen"](self.store, wvec)

    def vecget(self, wvec, index):
        return self.instance.exports(self.store)["vecget"](self.store, wvec, index)

    def vecset(self, wvec, index, wval):
        return self.instance.exports(self.store)["vecset"](self.store, wvec, index, wval)

    def vecpush(self, wvec, wval):
        return self.instance.exports(self.store)["vecpush"](self.store, wvec, wval)

    def vecpop(self, wvec):
        return self.instance.exports(self.store)["vecpop"](self.store, wvec)

    def vecunset(self, wvec, index):
        self.instance.exports(self.store)["vecunset"](self.store, wvec, index)


##############################################################################
# INSTANCE

class Instance:
    def __init__(self):
        self.iface = Iface()

    def symmap(self, symbols):
        return Symmap(self.iface, symbols)

    def parse(self, code):
        return Parsed(self.iface, code)


##############################################################################
# PARSED

class Parsed:
    def __init__(self, iface, code):
        wcode = iface.strdup(code)

        self.wast = iface.parse(wcode)
        self.iface = iface
        self.iface.free(wcode)

    def __del__(self):
        self.iface.astfree(self.wast)

    def eval(self, symmap=None):
        _symmap = Symmap(self.iface) if symmap is None else symmap

        if(_symmap.iface is self.iface):
            wvalue = self.iface.asteval(self.wast, _symmap.wsymmap)
            value = _getvalue(self.iface, wvalue)

            self.iface.valfree(wvalue)

            return value

        raise UsageError("Code and Symmap must be from the same JSONexpr Instance")


##############################################################################
# TYPES

class Symmap:
    def __init__(self, iface, symbols=None):
        self.iface = iface
        self.wsymmap = iface.newsym()

        if symbols:
            self.merge(symbols)

    def __del__(self):
        if self.wsymmap:
            self.iface.symfree(self.wsymmap)

        self.wsymmap = None

    def __contains__(self, name):
        wname = self.iface.strdup(name)
        wvalue = self.iface.symget(self.wsymmap, wname)

        self.iface.free(wname)
        # wvalue is a pointer to a value in wsymmap; do not free

        return wvalue != 0

    def __getitem__(self, name):
        wname = self.iface.strdup(name)
        wvalue = self.iface.symget(self.wsymmap, wname)
        value = _getvalue(self.iface, wvalue)

        self.iface.free(wname)
        # wvalue is a pointer to a value in wsymmap; do not free

        return value

    def __setitem__(self, name, value):
        wname = self.iface.strdup(name)
        wvalue = _mkvalue(self.iface, value)

        self.iface.symset(self.wsymmap, wname, wvalue)

        # wname and wvalue are now in wsymmap; do not free

        return value

    def __delitem__(self, name):
        wname = self.iface.strdup(name)

        self.iface.symunset(self.wsymmap, wname)
        self.iface.free(wname)

    def merge(self, dict_):
        for name,value in dict_.items():
            self.__setitem__(name, value)

class Map:
    def __init__(self, iface, wmap):
        self.iface = iface
        self.wmap = iface.valdup(wmap)

    def __del__(self):
        self.iface.valfree(self.wmap)

    def __contains__(self, name):
        wname = self.iface.strdup(name)
        wvalue = self.iface.mapget(self.wmap, wname)

        self.iface.free(wname)
        # wvalue is a pointer to a value in wmap; do not free

        return wvalue != 0

    def __getitem__(self, name):
        wname = self.iface.strdup(name)
        wvalue = self.iface.mapget(self.wmap, wname)
        value = _getvalue(self.iface, wvalue)

        self.iface.free(wname)
        # wvalue is a pointer to a value in wmap; do not free

        if not wvalue:
            raise KeyError(name)

        return value

    def __setitem__(self, name, value):
        wname = self.iface.strdup(name)
        wvalue = _mkvalue(self.iface, value)

        self.iface.mapset(self.wmap, wname, wvalue)

        # wname and wvalue are now in wmap; do not free

        return value

    def __delitem__(self, name):
        wname = self.iface.strdup(name)

        self.iface.mapunset(self.wmap, wname)
        self.iface.free(wname)

    def __len__(self):
        return self.iface.maplen(self.wmap)

    def __str__(self):
        wqstr = self.iface.valtoqstr(self.wmap)
        qstr = self.iface.strat(wqstr)

        self.iface.free(wqstr)

        return qstr

    def items(self):
        i = self.iface.mapbegin(self.wmap)
        j = self.iface.mapend(self.wmap)

        while i != j:
            wkey = self.iface.mapgetkey(self.wmap, i)
            wvalue = self.iface.mapgetval(self.wmap, i)
            key = self.iface.strat(wkey)
            value = _getvalue(self.iface, wvalue)

            yield (key,value)

            # wname and wvalue are pointers into wmap; do not free
            i = self.iface.mapnext(self.wmap, i)

    def toDict(self):
        result = {}

        for key,value in self.items():
            result[key] = value

        return result

class Vec:
    def __init__(self, iface, wvec):
        self.iface = iface
        self.wvec = iface.valdup(wvec)

    def __del__(self):
        self.iface.valfree(self.wvec)

    def __getitem__(self, index):
        wvalue = self.iface.vecget(self.wvec, index)
        value = _getvalue(self.iface, wvalue)

        # wvalue is a pointer to a value in wvec; do not free

        if not wvalue:
            raise KeyError(name)

        return value

    def __setitem__(self, index, value):
        wvalue = _mkvalue(self.iface, value)

        self.iface.vecset(self.wvec, index, wvalue)

        # wvalue is now in wvec; do not free

        return value

    def __delitem__(self, index):
        self.iface.vecunset(self.wvec, index)

    def __len__(self):
        return self.iface.veclen(self.wvec)

    def __str__(self):
        wqstr = self.iface.valtoqstr(self.wvec)
        qstr = self.iface.strat(wqstr)

        self.iface.free(wqstr)

        return qstr

    def toList(self):
        result = []

        for i in range(self.__len__()):
            result += [self.__getitem__(i)]

        return result


##############################################################################
# JSON ENCODER

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Map): return obj.toDict()
        if isinstance(obj, Vec): return obj.toList()

        return super().default(obj)


##############################################################################
# PRIVATE FUNCTIONS

def _getvalue(iface, wvalue):
    value = None

    if wvalue:
        value_t = iface.valtype(wvalue)

        if   value_t == "OBJECT" : value = Map(iface, wvalue)
        elif value_t == "ARRAY"  : value = Vec(iface, wvalue)
        else                     :
            wqstr = iface.valtoqstr(wvalue)
            qstr = iface.strat(wqstr)
            value = json.loads(qstr)

            iface.free(wqstr)

    return value

def _mkvalue(iface, value):
    if   isinstance(value, dict):
        wvalue = iface.mapval()

        for k,v in value.items():
            iface.mapset(wvalue, iface.strdup(str(k)), _mkvalue(iface, v))

    elif isinstance(value, list):
        wvalue = iface.vecval()

        for v in value:
            iface.vecpush(wvalue, _mkvalue(iface, v))

    elif value is None              : wvalue = iface.nullval()
    elif isinstance(value, bool)    : wvalue = iface.boolval(value)
    elif isinstance(value, int)     : wvalue = iface.i64val(value)
    elif isinstance(value, float)   : wvalue = iface.f64val(value)
    elif isinstance(value, Map)     : wvalue = iface.valdup(value.wmap)
    elif isinstance(value, Vec)     : wvalue = iface.valdup(value.wvec)
    else                            : wvalue = iface.strval(iface.strdup(str(value)))

    return wvalue


##############################################################################
# PUBLIC EXCEPTIONS

class JeException(Exception):
    def __init__(self, text):
        super().__init__(text)

class UsageError(JeException):
    def __init__(self, text):
        self.text = text

class SyntaxError(JeException):
    def __init__(self, text):
        self.text = text

class Exit(JeException):
    def __init__(self, code):
        self.code = code


##############################################################################
# PUBLIC FUNCTIONS

def instance():
    return Instance()

def eval(code, symbols=None):
    instance = Instance()
    parsed = instance.parse(str(code))
    symmap = instance.symmap(symbols)

    return parsed.eval(symmap)

def evalfile(path, symbols=None):
    data = ""

    with open(path, "r") as fd:
        data = fd.read()

    return eval(data, symbols)


# vim:ft=python:
