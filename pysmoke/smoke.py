
from _smoke import ffi, smokec, bindings


def Args(n):
    return ffi.new('StackItem[%d]'%n)

def delete_callback(func):
    return ffi.callback('void(CSmokeBinding,Index,void*)', func)

def method_call_handler(func):
    return ffi.callback('int(CSmokeBinding,Index,void*,Stack,int)', func)

def class_name_handler(func):
    return ffi.callback('char*(CSmokeBinding,Index)', func)



def ClassDef(object):

    def __init__(self, moduleindex):
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        self._index = moduleindex.index
        self._classdef = smokec.Smoke_classes(self._smoke)[self._index]

    @property
    def name(self):
        return ffi.string(self._classdef.className)

    @property
    def is_external(self):
        """ whether it is defined in another module. """
        return bool(self._classdef.external)

    @property
    def bases(self):
        pass

    def _call(self, index, inst, args):
        pass

    @property
    def has_ctor(self):
        return self._classdef.flags & smokec.cf_constructor

    @property
    def has_deepcopy(self):
        return self._classdef.flags & smokec.cf_deepcopy

    @property
    def has_virtual(self):
        """ Has a virtual destructor """
        return self._classdef.flags & smokec.cf_virtual

    @property
    def is_namespace(self):
        """ whether it is a namespace """
        return self._classdef.flags & smokec.cf_namespace

    @property
    def is_undefined(self):
        """ whether it is defined elsewhere """
        return self._classdef.flags & smokec.cf_undefined


class MethodDef(object):
    def __init__(self, moduleindex):
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        self._index = moduleindex.index
        self._methoddef = smokec.Smoke_methods(self._smoke)[self._index]
        self._class = ClassDef(ffi.new('CModuleIndex', [self._smoke, self._methoddef.classId]))

    @property
    def cls(self):
        return self._class

    @property
    def name(self):
        return ffi.string(smokec.Smoke_methodNames(self._smoke)[self._methoddef.name])

    @property
    def args(self):
        pass




class Smoke(object):
    def __init__(self, csmoke):
        self.csmoke = csmoke


class Binding(object):
    def __init__(self, smoke, delete_handler, method_call_handler, class_name_handler):
        self._smoke = smoke
        self._delete_handler = delete_handler
        self._method_call_handler = method_call_handler
        self._class_name_handler = class_name_handler

    def on_delete(self):
        return self._delete_handler()

    def on_method_call(self):
        return self._method_call_handler()

    def on_class_name(self):
        return self._class_name_handler()

    @classmethod
    def find_class(cls, class_name):
        pass

    def find_method(self, klass, method_name):
        if not isinstance(klass, basestring):
            klass = klass.name
        return self._smoke.find_method(klass, method_name)



