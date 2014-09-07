from __future__ import print_function, absolute_import

import importlib
import keyword
import sys
from types import ModuleType

from .smoke import Smoke, Binding, smokec, bindings, Type, TypedValue, dbg


KWMAP = {kw+'_':kw for kw in keyword.kwlist + [
    'print', 'exec']} # For the benefit of python3


class SmokeMethodDescr(object):
    __slots__ = ('cls', 'name')

    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def __get__(self, inst, typ=None):
        call = typ.__classdef__.call
        print('get methdescr:', inst, typ, self.cls, self.name)
        return self._get_method(inst, typ)

    def _get_method(self, inst, typ=None):
        def method(*args, **kwds):
            return self._method_call(inst, typ, *args, **kwds)
        method.__name__ = self.name
        return method

    def _method_call(self, inst, cls, *args, **kwds):
        called_from_inst = inst is not None
        name = self.name
        call = cls.__classdef__.call
        constructor = name == cls.__name__
        metacls = type(cls)
        if called_from_inst:
            # Try bound method first, call would handle static method
            cargs = metacls._get_sargs(args)
            cinst = metacls._get_inst(inst)
            ret = call(name, cinst, cargs, kwds)
            ret = metacls._get_retval(ret)
        elif constructor:
            # constructor logic
            cargs = metacls._get_sargs(args)
            cinst = metacls._get_inst(inst)
            ret = call(name, cinst, cargs, kwds)
            # Dont convert return value
        else:
            # If first arg matches typ, try bound method
            try_static = True
            if len(args) > 0 and isinstance(args[0], cls):
                cargs = metacls._get_sargs(args[0])
                cinst = metacls._get_inst(args[1:])
                try:
                    ret = call(name, inst, args, kwds)
                except ValueError:
                    pass
                else:
                    try_static = False
                    ret = metacls._get_retval(ret)
            if try_static:
                cargs = metacls._get_sargs(args)
                ret = call(name, None, cargs, kwds)
                ret = metacls._get_retval(ret)
        return ret


class SmokeMetaClass(type):
    __classes_map__ = {}

    def __init__(cls, name, bases, attrs):
        print('creating cls', cls.__name__, name)
        cls.__classdef__ = Binding.find_class(name)

    @classmethod
    def _get_inst(metacls, inst):
        if isinstance(inst, SmokeClass):
            inst = inst.__cval__
        return inst

    @classmethod
    def _get_sargs(metacls, args):
        sargs = []
        for arg in args:
            if isinstance(arg, SmokeClass):
                sargs.append(arg.__cval__)
            else:
                sargs.append(arg)
        return sargs

    @classmethod
    def _get_retval(metacls, ret):
        if isinstance(ret, TypedValue):
            if ret.typ.cls is not None:
                retcls = SmokeMetaClass.get_class(ret.typ.cls.name, ret.typ.cls.binding)
                print('retcls:', retcls)
                retobj = retcls.__new__(retcls)
                retobj.__cval__ = ret
                ret = retobj
        return ret

    @classmethod
    def _get_method(metacls, cls, name):
        # UNUSED: replaced with _get_method2
        call = cls.__classdef__.call
        constructor = name == cls.__name__
        def method(inst, *args, **kwds):
            args = metacls._get_sargs(args)
            inst = metacls._get_inst(inst)
            ret = call(name, inst, args, kwds)
            if not constructor:
                ret = metacls._get_retval(ret)
            return ret
        method.__name__ = cls.__name__ + '.' + name
        if constructor:
            method = staticmethod(method)
        elif cls.__classdef__.is_static_method(name):
            method = classmethod(method)
        return method

    @classmethod
    def _get_method2(metacls, cls, name):
        return SmokeMethodDescr(cls, name)

    def __getattr__(cls, name):
        #clsdef = super(SmokeClass, self).__getattribute__('__classdef__')
        print('SMC getattr:', cls, name)
        # Handle renamed keyword functions
        #ret = cls._get_method(cls, name)
        fname = KWMAP.get(name, name)
        ret = cls._get_method2(cls, fname)
        setattr(cls, name, ret)
        return getattr(cls, name)

    def y__call__(cls, *args, **kwds):
        """ Constructor method of the class """
        return getattr(cls, cls.__classdef__.name)(*args, **kwds)

    @classmethod
    def get_class(metacls, name, binding):
        if name in metacls.__classes_map__:
            return metacls.__classes_map__[name]
        else:
            # from IPython.core.debugger import Tracer; Tracer()()
            ret = metacls(name, (SmokeClass,), {})
            ret.__module__ = binding.name
            print('get_class:', name, ret, ret.__module__)
            metacls.__classes_map__[name] = ret
            return ret

    @classmethod
    def wrap_cdata(metacls, typ, cdata):
        ret = typ.cls.__new__(typ.cls)
        return ret


SmokeSuperClass = SmokeMetaClass('SmokeSuperClass', (object,), {
    '__doc__':''' Base class for Smoke classes.
                 
                 Only purpose is working around metaclass declaration
                 difference between python 2 and python 3
                 '''})


class SmokeClass(SmokeSuperClass):
    """ Wrapper classes should not maintain state apart from __cval__.
    User subclasses can do as they please.
    """
    def __init__(self, *args, **kwds):
        cls = type(self)
        cval = getattr(cls, cls.__classdef__.name)(*args, **kwds)
        print('cval:', cval, self, args, kwds)
        self.__cval__ = cval

    def __getattr__(self, name):
        print('SC getattr:', self, name)
        cls = type(self)
        ret = getattr(cls, name)
        return getattr(self, name)



class SmokeClassDescr(object):
    __slots__ = ()

    def __get__(self, obj, typ=None):
        if obj is None:
            return self
        else:
            pass


class SmokeModule(ModuleType):
    def __init__(self, binding, package):
        self.__binding__ = binding
        self.__pkg__ = package
        super(SmokeModule, self).__init__(package)

    def __getattr__(self, name):
        binding = self.__binding__
        # TODO: Return overridden class
        print('cls_mod', self.__pkg__)
        try:
            cls_mod = importlib.import_module('%s.%s' % (self.__pkg__, name))
            cls_mod.__package__ = __package__ + '.' + self.__binding__.name
        except ImportError as e:
            print('e')
            return SmokeMetaClass.get_class(name, binding)
        else:
            cls = getattr(cls_mod, name)
            cls.__module__ = cls_mod.__package__
            pkg = sys.modules[self.__pkg__]
            # Setattr needed because import mechanism automatically sets
            # the module attribute on parent module
            setattr(pkg, name, cls)
            return cls

    @classmethod
    def get_module(cls, binding, pkg):
        mod = cls(binding, pkg)
        return mod


