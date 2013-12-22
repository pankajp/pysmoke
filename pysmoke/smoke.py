from __future__ import print_function, absolute_import

import sys

from ._smoke import ffi, smokec, bindings, pystring
from . import marshal

def Args(n):
    return ffi.new('StackItem[%d]' % n)

def CModuleIndex(smokec, index):
    return ffi.new('CModuleIndex*', [smokec, index])[0]

def get_args(*args):
    cargs = Args(len(args)+1)
    for i, arg in enumerate(args):
        cargs[i+1].s_voidp = arg
    return cargs


def delete_callback(func):
    return ffi.callback('void(CSmokeBinding,Index,void*)', func)

def method_call_callback(func):
    return ffi.callback('cbool(CSmokeBinding,Index,void*,Stack,cbool)', func)

def class_name_callback(func):
    return ffi.callback('char*(CSmokeBinding,Index)', func)


class Type(object):
    def __init__(self, binding, ctype):
        self.binding = binding
        self._smoke = binding.smoke
        self._type = ctype

    @property
    def name(self):
        return pystring(self._type.name)

    @property
    def cls(self):
        if self._type.classId < 0:
            return None
        elif self._type.classId == 0:
            print('Bindings for class:', self.name, 'not in smoke; marshallers have to be written')
            return
        return ClassDef(self.binding,
                        CModuleIndex(self._smoke, self._type.classId))

    @property
    def type_id(self):
        return self._type.flags & smokec.tf_elem

    @property
    def stacktype(self):
        return {smokec.tf_stack:'stack',
                smokec.tf_ptr:'ptr',
                smokec.tf_ref:'ref'}[self._type.flags & 0x30]

    @property
    def is_const(self):
        return bool(self._type.flags & smokec.tf_const)

    @classmethod
    def from_cls(cls, klass):
        ctype = ffi.new('Type*', [ffi.new('char[]', klass.name.encode('ascii')+b'*'),
                                  klass._index,
                                  smokec.t_class + smokec.tf_ptr])
        return cls(klass.binding, ctype)

    def __str__(self):
        return 'Type("%s")' % (self.name)

    __repr__ = __str__


class TypedValue(object):
    def __init__(self, value, typ):
        self.value = value
        self.typ = typ

    def __str__(self):
        return 'TypedValue(<%s> object %s)' % (self.typ, self.value)

    __repr__ = __str__


class ClassDef(object):

    def __init__(self, binding, moduleindex):
        self.binding = binding
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        self._index = moduleindex.index
        self._classdef = smokec.Smoke_classes(self._smoke)[self._index]

    @property
    def name(self):
        return pystring(self._classdef.className)

    @property
    def full_name(self):
        return '%s.%s' % (self.binding.name, self.binding.class_name(self))

    @property
    def is_external(self):
        """ whether it is defined in another module. """
        return bool(self._classdef.external)

    @property
    def bases(self):
        csmoke = self._smoke
        bases = []
        bases_list = smokec.Smoke_inheritanceList(csmoke)
        baseidx = self._classdef.parents
        while bases_list[baseidx] != 0:
            cmi = CModuleIndex(csmoke, bases_list[baseidx])
            cls = ClassDef(self.binding, cmi)
            if cls.is_external:
                cls = self.binding.find_class(cls.name)
            bases.append(cls)
            baseidx += 1
        return bases

    def is_subclassof(self, other):
        return smokec.isDerivedFromI(self._smoke, self._index, other._smoke, other._index)

    def find_method(self, name, ambiguous=True, munged=True):
        if not munged:
            mnames = self.find_munged_names(name)
            methods = []
            for mname in mnames:
                submethods = self.find_method(mname, ambiguous, True)
                # should not be None
                if isinstance(submethods, MethodDef):
                    methods.append(submethods)
                elif submethods is not None:
                    methods.extend(submethods)
                else:
                    raise ValueError('Not such method: %s' % name)
                if not ambiguous and len(methods) > 1:
                    raise ValueError('Ambiguous method overload: %s' % name)
            return methods
        mmethid = smokec.Smoke_findMethod(self._smoke, self.name.encode('ascii'), name.encode('ascii'))
        methodmap = smokec.Smoke_methodMaps(mmethid.smoke)
        mmap = methodmap[mmethid.index]
        classes = smokec.Smoke_classes(mmethid.smoke)
        if mmap.method > 0:
            if classes[mmap.classId].external:
                cls = self.binding.find_class(pystring(classes[mmap.classId].name))
                return cls.find_method(name)
            return MethodDef(self.binding.get_binding(mmethid.smoke.smoke),
                             CModuleIndex(mmethid.smoke,
                                          mmap.method))
        elif mmap.method < 0:
            if ambiguous:
                aidx = -mmap.method
                amethods = smokec.Smoke_ambiguousMethodList(self._smoke)
                methods = []
                while amethods[aidx] != 0:
                    methidx = amethods[aidx]
                    methods.append(MethodDef(self.binding.get_binding(mmethid.smoke.smoke),
                                             CModuleIndex(mmethid.smoke,
                                                          methidx)))
                    aidx += 1
                return methods
            else:
                raise ValueError('Ambiguous method overload: %s' % name)
        else:
            return None

    def find_method_by_args(self, name, args=[], kwds={}):
        if kwds:
            raise NotImplementedError('keyword arguments not implemented')
        match = None
        # FIXME: Find best matching method instead of first match
        match_score = -1
        for method in self.iter_methods():
            print(method.name, name)
            if method.name == name:
                meth_args = method.args
                print(len(meth_args), len(args))
                if len(meth_args) != len(args):
                    continue
                for i, arg in enumerate(args):
                    if not self.binding.is_compatible_type(meth_args[i], arg):
                        break
                else:
                    match = method
                    return match
                    continue
                break

    def find_munged_names(self, name):
        namemid = smokec.Smoke_idMethodName(self._smoke, name.encode('ascii'))
        nameid = namemid.index
        mnames = set()
        if nameid != 0:
            mmaps = smokec.Smoke_methodMaps(self._smoke)
            methodnames = smokec.Smoke_methodNames(self._smoke)
            for i in range(1, smokec.Smoke_numMethodMaps(self._smoke)):
                mmap = mmaps[i]
                mname = pystring(methodnames[mmap.name])
                if mmap.classId == self._index and mname.rstrip('$#?') == name:
                    mnames.add(mname)

        for base in self.bases:
            mnames.update(base.find_munged_names(name))
        return list(mnames)

    def iter_methods(self, inherited=True):
        csmoke = self._smoke
        clsidx = self._index
        methods = smokec.Smoke_methods(csmoke)
        for i in range(1, smokec.Smoke_numMethods(csmoke)):
            if methods[i].classId == clsidx:
                cmi = CModuleIndex(csmoke, i)
                yield MethodDef(self.binding, cmi)

        if inherited:
            for base in self.bases:
                for meth in base.iter_methods():
                    yield meth

    def is_static_method(self, name):
        for meth in self.find_method(name, munged=False):
            return meth.is_static
        raise AttributeError('no such method: %s of %s' % (name, self))

    def call(self, meth_name, inst, args, kwds):
        meth = self.find_method_by_args(meth_name, args, kwds)
        if meth is None:
            raise AttributeError('no suitable method: %s of %s: %s,%s' % (meth_name, self, args, kwds))
        return meth.call(inst, *args, **kwds)

    def call_method(self, meth, inst, args, kwds):
        print('calling:', meth, meth.cls._classdef, meth._methoddef, meth.binding, meth.cls.binding)
        convargs = []
        for i, arg in enumerate(args):
            convargs.append(self.binding.from_py(arg, meth.args[i]))
        cargs = get_args(*(args+(ffi.NULL, ffi.NULL)))
        if meth.is_static or meth.is_ctor:
            cinst = ffi.NULL
        else:
            cinst = self.binding.from_py(inst, Type.from_cls(self))
        meth.cls._classdef.classFn(meth._methoddef.method, cinst, cargs)
        ret = cargs[0]
        if meth.is_ctor:
            # Constructor.
            # method index 0 is always "set smoke binding" - needed for
            # virtual method callbacks etc.
            cargs[1].s_voidp = meth.cls.binding.cbinding.binding
            meth.cls._classdef.classFn(0, ret.s_voidp, cargs)
        print('return from:', meth, ret.s_voidp)
        return self.binding.to_py(ret.s_voidp, meth.rettype)

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

    def __str__(self):
        return 'ClassDef(%s.%s)' % (self.binding.name,
                                    self.binding.class_name(self))

    __repr__ = __str__


class MethodDef(object):
    def __init__(self, binding, moduleindex):
        self.binding = binding
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        self._index = moduleindex.index
        self._methoddef = smokec.Smoke_methods(self._smoke)[self._index]
        self._class = ClassDef(self.binding, CModuleIndex(self._smoke, self._methoddef.classId))

    @property
    def cls(self):
        return self._class

    @property
    def name(self):
        return pystring(smokec.Smoke_methodNames(self._smoke)[self._methoddef.name])

    @property
    def full_name(self):
        return '%s.%s' % (self.cls.full_name, self.name)

    @property
    def args(self):
        ret = []
        argsidx = self._methoddef.args
        argslist = smokec.Smoke_argumentList(self._smoke)
        types = smokec.Smoke_types(self._smoke)
        for i in range(argsidx, argsidx+self._methoddef.numArgs):
            typidx = argslist[i]
            typ = types[typidx]
            ret.append(Type(self.binding, typ))
        return tuple(ret)

    @property
    def rettype(self):
        return Type(self._smoke, smokec.Smoke_types(self._smoke)[self._methoddef.ret])

    def call(self, inst, *args, **kwds):
        return self.cls.call_method(self, inst, args, kwds)

    @property
    def is_static(self):
        return self._methoddef.flags & smokec.mf_static

    @property
    def is_const(self):
        return self._methoddef.flags & smokec.mf_const

    @property
    def is_copyctor(self):
        return self._methoddef.flags & smokec.mf_copyctor

    @property
    def is_internal(self):
        return self._methoddef.flags & smokec.mf_internal

    @property
    def is_enum(self):
        return self._methoddef.flags & smokec.mf_enum

    @property
    def is_ctor(self):
        return self._methoddef.flags & smokec.mf_ctor

    @property
    def is_dtor(self):
        return self._methoddef.flags & smokec.mf_dtor

    @property
    def is_protected(self):
        return self._methoddef.flags & smokec.mf_protected

    @property
    def is_attribute(self):
        return self._methoddef.flags & smokec.mf_attribute

    @property
    def is_property(self):
        return self._methoddef.flags & smokec.mf_property

    @property
    def is_virtual(self):
        return self._methoddef.flags & smokec.mf_virtual

    @property
    def is_purevirtual(self):
        return self._methoddef.flags & smokec.mf_purevirtual

    @property
    def is_signal(self):
        return self._methoddef.flags & smokec.mf_signal

    @property
    def is_slot(self):
        return self._methoddef.flags & smokec.mf_slot

    @property
    def is_explicit(self):
        return self._methoddef.flags & smokec.mf_explicit

    def __str__(self):
        return 'MethodDef(%s.%s%s)' % (self.binding.class_name(self.cls),
                                         self.name, self.args)

    __repr__ = __str__


class Converter(object):
    _obj_map = {}

    def __init__(self, binding):
        self.binding = binding

    def is_compatible_type(self, required, given):
        if isinstance(given, TypedValue):
            if given.typ.cls and given.typ.cls.is_subclassof(required):
                return True
        elif isinstance(given, {smokec.t_voidp:(ffi.CData),
                                smokec.t_bool:(bool, int),
                                smokec.t_char:(str),
                                smokec.t_uchar: (int, str),
                                smokec.t_short:(int),
                                smokec.t_ushort:(int),
                                smokec.t_int:(int),
                                smokec.t_uint:(int),
                                smokec.t_long:(int),
                                smokec.t_ulong:(int),
                                smokec.t_float:(int, float),
                                smokec.t_double:(int, float),
                                smokec.t_enum:(int),
                                }.get(required.type_id, ())):
            return True
        elif isinstance(given, {'const char*':(str),
                                'char*':(str),
                                }.get(required.name, ())):
            return True
        return False

    def to_py(self, obj, typ):
        primitive = {
                     smokec.t_bool:bool,
                     smokec.t_char:int,
                     smokec.t_uchar:int,
                     smokec.t_short:int,
                     smokec.t_ushort:int,
                     smokec.t_int:int,
                     smokec.t_uint:int,
                     smokec.t_long:int,
                     smokec.t_ulong:int,
                     smokec.t_float:float,
                     smokec.t_double:float,
                     smokec.t_enum:int,
                     }.get(typ.type_id)
        if primitive:
            return primitive(obj)
        if isinstance(obj, TypedValue):
            # FIXME: error if obj.typ not derived from typ
            if obj.typ._type.classId == 0:
                print('FIXME: %s not included in smoke, bindings to be written'%
                      obj.typ.name)
            return obj
        if typ._type.classId == 0:
            conv = getattr(marshal, typ.name, None)
            if conv is None:
                print('FIXME: %s not included in smoke, bindings to be written'%
                      typ.name)
            else:
                return conv.to_py(obj)
        print('could not convert to py:', obj, typ)
        return TypedValue(obj, typ)

    def from_py(self, obj, typ):
        primitive = {
                     smokec.t_bool:'CBool',
                     smokec.t_char:'char',
                     smokec.t_uchar:'unsigned char',
                     smokec.t_short:'short',
                     smokec.t_ushort:'unsigned short',
                     smokec.t_int:'int',
                     smokec.t_uint:'unsigned int',
                     smokec.t_long:'long',
                     smokec.t_ulong:'unsingned long',
                     smokec.t_float:'float',
                     smokec.t_double:'double',
                     smokec.t_enum:'int',
                     }.get(typ.type_id)
        if primitive:
            return ffi.new(primitive, typ)
        if obj is None:
            return ffi.NULL
        if typ._type.classId == 0:
            conv = getattr(marshal, typ.name, None)
            if conv is None:
                print('FIXME: %s not included in smoke, bindings to be written'%
                      typ.name)
            else:
                return conv.from_py(obj)
        if isinstance(obj, TypedValue):
            # FIXME: cast/check compatibility of the two types
            obj = obj.value
        if not isinstance(obj, ffi.CData):
            print('could not convert from py:', obj, typ)
        return obj


class Smoke(object):
    def __init__(self, csmoke):
        self.csmoke = csmoke

    @property
    def name(self):
        return pystring(smokec.Smoke_moduleName(self.csmoke))

    def __str__(self):
        return 'Smoke(%s)' % (self.name)

    __repr__ = __str__


class Binding(object):
    bindings_map = {}

    def __init__(self, smoke):
        self.smoke = smoke
        self.converter = Converter(self)
        if smoke.csmoke.smoke in self.bindings_map:
            raise ValueError('binding already registered for: %s' % smoke)
        self.bindings_map[smoke.csmoke.smoke] = self
        self.name = self.smoke.name
        self._c_handlers = [delete_callback(self._on_delete),
                            method_call_callback(self._on_method_call),
                            class_name_callback(self._on_class_name)]
        self.cbinding = smokec.SmokeBinding_new(
            self.smoke.csmoke,
            self._c_handlers[0],
            self._c_handlers[1],
            self._c_handlers[2])

    def _on_delete(self, csmokebinding, clsid, obj):
        cmi = CModuleIndex(smokec.CSmoke_FromBinding(csmokebinding), clsid)
        cls = ClassDef(self, cmi)
        return self.delete_handler(cls, obj)

    def delete_handler(self, cls, obj):
        print('deleted:', cls.name, obj)
        return 0

    def _on_method_call(self, csmokebinding, methidx, cobj, cargs, is_abstract):
        cmi = CModuleIndex(smokec.CSmoke_FromBinding(csmokebinding), methidx)
        meth = MethodDef(self.bindings_map[cmi.smoke.smoke], cmi)
        obj = self.to_py(cobj, Type.from_cls(meth.cls))
        args = []
        for i, arg in enumerate(meth.args):
            args.append(self.to_py(cargs[i+1], arg))
        handled, ret = self.method_call_handler(meth.cls, obj, meth, args, is_abstract)
        if handled:
            cret = self.from_py(cobj, meth.rettype)
            set_stackitem_value(cargs[0], cret, meth.rettype)
        return int(handled)

    def method_call_handler(self, cls, obj, method, args, is_abstract):
        print('method_call: %s::%s()' % (cls.name, method.name))
        # FIXME: do blah
        return False, None

    def _on_class_name(self, csmokebinding, clsid):
        cmi = CModuleIndex(smokec.CSmoke_FromBinding(csmokebinding), clsid)
        cls = ClassDef(self, cmi)
        return self.class_name_handler(cls)

    def class_name_handler(self, cls):
        return cls.name.replace('::', '.')

    class_name = class_name_handler

    @classmethod
    def get_binding(cls, smokep):
        if smokep in cls.bindings_map:
            return cls.bindings_map[smokep]
        smokec = ffi.new('CSmoke*', [smokep])[0]
        binding = cls(Smoke(smokec))
        cls.bindings_map[smokep] = binding
        return binding

    @classmethod
    def find_class(cls, class_name):
        """ Handles classes defined in different modules """
        class_name = class_name.encode('ascii')
        clsid = smokec.findClass(class_name)
        print('find_class clsid:', class_name, clsid)
        if clsid.index == 0:
            return None
        return ClassDef(cls.get_binding(clsid.smoke.smoke), clsid)

    def iter_classes(self):
        csmoke = self.smoke.csmoke
        for i in range(1, smokec.Smoke_numClasses(csmoke)):
            cmi = CModuleIndex(csmoke, i)
            cls = ClassDef(self, cmi)
            yield cls

    def cast(self, obj, from_cls, to_cls):
        smokec.Smoke_castFn(self.smoke.smokec)(obj, from_cls, to_cls)

    def is_compatible_type(self, required, given):
        """ Check whether the given types are compatible with the required types.
        required is a `Type` object """
        #from IPython.core.debugger import Tracer; Tracer()()
        return self.converter.is_compatible_type(required, given)

    def to_py(self, obj, typ):
        return self.converter.to_py(obj, typ)

    def from_py(self, obj, typ):
        return self.converter.from_py(obj, typ)

    def __str__(self):
        return 'Binding(%s)' % (self.name)

    __repr__ = __str__

