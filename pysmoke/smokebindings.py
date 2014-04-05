from __future__ import print_function, absolute_import

import importlib
import keyword

from .smoke import Smoke, Binding, smokec, bindings, Type, TypedValue, dbg


KWMAP = {kw+'_':kw for kw in keyword.kwlist + [
    'print', 'exec']} # For the benefit of python3


def qtcore_smoke():
    return Binding.get_binding(bindings.qtcore_CSmoke().smoke)


def qtgui_smoke():
    return Binding.get_binding(bindings.qtgui_CSmoke().smoke)



binding_map = {'qtcore':qtcore_smoke,
               'qtgui':qtgui_smoke,
               }


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

    def __getattr__(cls, name):
        #clsdef = super(SmokeClass, self).__getattribute__('__classdef__')
        print('SMC getattr:', cls, name)
        try:
            ret = cls._get_method(cls, name)
        except AttributeError:
            # Handle renamed functions like exec -> exec_
            if name in KWMAP:
                ret = cls._get_method(cls, KWMAP[name])
            else:
                raise
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
            ret = metacls(name, (SmokeClass,), {})
            ret.__module__ += '.' + binding.name
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
        cval = getattr(cls, cls.__classdef__.name)(cls, *args, **kwds)
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


class SmokeModule(object):
    __binding_map__ = {}
    def __init__(self, binding):
        self.__binding__ = binding

    def __getattr__(self, name):
        binding = self.__binding__
        # TODO: Return overridden class
        print('cls_mod', __package__)
        try:
            cls_mod = importlib.import_module('.%s.%s' % (self.__binding__.name, name),
                                              __package__)
            cls_mod.__package__ = __package__ + '.' + self.__binding__.name
        except ImportError as e:
            print('e')
            return SmokeMetaClass.get_class(name, binding)
        else:
            cls = getattr(cls_mod, name)
            cls.__module__ = cls_mod.__package__
            return cls

    @classmethod
    def get_module(cls, name):
        if name in cls.__binding_map__:
            return cls.__binding_map__[name]
        else:
            binding = binding_map[name]()
            ret = cls(binding)
            cls.__binding_map__[name] = ret
            return ret



QtCore = SmokeModule.get_module('qtcore')
QtGui = SmokeModule.get_module('qtgui')


