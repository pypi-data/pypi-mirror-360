__copyright__ = "Copyright 2024-2025 Mark Kim"
__license__ = "Apache 2.0"
__version__ = "0.2.4"
__author__ = "Mark Kim"

import re
import os
import json
import wasmer
import importlib.util

if importlib.util.find_spec("wasmer_compiler_llvm") is not None:
    import wasmer_compiler_llvm
else:
    import wasmer_compiler_cranelift


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
        # Load jsonexpr
        with open(WASMFILE, mode="rb") as fd:
            self.store = wasmer.Store()
            self.module = wasmer.Module(self.store, fd.read())

        # Instantiate
        self.instance = wasmer.Instance(self.module, {
            "env": {
                "read"   : wasmer.Function(self.store, self.read),
                "write"  : wasmer.Function(self.store, self.write),
                "_exit"  : wasmer.Function(self.store, self._exit),
            }
        })

        # Cache memory
        self.memory8 = self.instance.exports.memory.uint8_view()

    def read(self, fd:"i32", buf:"i32", count:"i32") -> "i32":
        data = os.read(fd, count)
        count = len(data)
        self.memory8[buf:buf+count] = data

        return count

    def write(self, fd:"i32", buf:"i32", count:"i32") -> "i32":
        return os.write(fd, bytearray(self.memory8[buf:buf+count]))

    def _exit(self, status:"i32") -> None:
        raise Exit(status)

    def strat(self, waddr):
        count = 0

        while(self.memory8[waddr+count] != 0):
            count += 1

        return bytearray(self.memory8[waddr:waddr+count]).decode("utf-8")

    def strdup(self, string):
        encoded = string.encode("utf-8")
        waddr = self.instance.exports.calloc(1, len(encoded)+1)
        self.memory8[waddr:waddr+len(string)] = encoded
        self.memory8[waddr+len(encoded)] = 0

        return waddr

    def free(self, waddr):
        self.instance.exports.free(waddr)

    def parse(self, wcode):
        return self.instance.exports.parse(wcode)

    def asteval(self, wast, wsymmap):
        return self.instance.exports.asteval(wast, wsymmap)

    def astfree(self, wast):
        self.instance.exports.astfree(wast)

    def newsym(self, wparent=0):
        return self.instance.exports.newsym(wparent)

    def symget(self, wsymmap, wkey):
        return self.instance.exports.symget(wsymmap, wkey)

    def symset(self, wsymmap, wkey, wvalue):
        return self.instance.exports.symset(wsymmap, wkey, wvalue, 0)

    def symfree(self, wsymmap):
        return self.instance.exports.symfree(wsymmap)

    def nullval(self):
        return self.instance.exports.nullval()

    def boolval(self, _bool):
        return self.instance.exports.boolval(_bool)

    def i64val(self, i64):
        return self.instance.exports.i64val(i64)

    def f64val(self, f64):
        return self.instance.exports.f64val(f64)

    def strval(self, wcstr):
        return self.instance.exports.strval(wcstr)

    def mapval(self):
        return self.instance.exports.mapval()

    def vecval(self):
        return self.instance.exports.vecval()

    def valdup(self, wval):
        return self.instance.exports.valdup(wval)

    def valtype(self, wval):
        return self.strat(self.instance.exports.valtype(wval))

    def valfree(self, wval):
        self.instance.exports.valfree(wval)

    def valtobool(self, wval):
        return self.instance.exports.valtobool(wval)

    def valtoi64(self, wval):
        return self.instance.exports.valtoi64(wval)

    def valtof64(self, wval):
        return self.instance.exports.valtof64(wval)

    def valtocstr(self, wval):
        return self.instance.exports.valtocstr(wval)

    def valtoqstr(self, wval):
        return self.instance.exports.valtoqstr(wval)

    def maplen(self, wmap):
        return self.instance.exports.maplen(wmap)

    def mapget(self, wmap, wkey):
        return self.instance.exports.mapget(wmap, wkey)

    def mapset(self, wmap, wkey, wval):
        return self.instance.exports.mapset(wmap, wkey, wval)

    def mapunset(self, wmap, wkey):
        self.instance.exports.mapunset(wmap, wkey)

    def mapbegin(self, wmap):
        return self.instance.exports.mapbegin(wmap)

    def mapend(self, wmap):
        return self.instance.exports.mapend(wmap)

    def mapnext(self, wmap, witer):
        return self.instance.exports.mapnext(wmap, witer)

    def mapgetkey(self, wmap, witer):
        return self.instance.exports.mapgetkey(wmap, witer)

    def mapgetval(self, wmap, witer):
        return self.instance.exports.mapgetval(wmap, witer)

    def veclen(self, wvec):
        return self.instance.exports.veclen(wvec)

    def vecget(self, wvec, index):
        return self.instance.exports.vecget(wvec, index)

    def vecset(self, wvec, index, wval):
        return self.instance.exports.vecset(wvec, index, wval)

    def vecpush(self, wvec, wval):
        return self.instance.exports.vecpush(wvec, wval)

    def vecpop(self, wvec):
        return self.instance.exports.vecpop(wvec)

    def vecunset(self, wvec, index):
        self.instance.exports.vecunset(wvec, index)


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
