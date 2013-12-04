from __future__ import print_function

from ._smoke import ffi, smokec, bindings


def Args(n):
    return ffi.new('StackItem[%d]'%n)

def CModuleIndex(smokec, index):
    return ffi.new('CModuleIndex*', [smokec, index])[0]

def get_args(*args):
    cargs = Args(len(args)+1)
    for i,arg in enumerate(args):
        cargs[i+1].s_voidp = arg
    return cargs


def delete_callback(func):
    return ffi.callback('void(CSmokeBinding,Index,void*)', func)

def method_call_callback(func):
    return ffi.callback('cbool(CSmokeBinding,Index,void*,Stack,cbool)', func)

def class_name_callback(func):
    return ffi.callback('char*(CSmokeBinding,Index)', func)

def pystring(charp):
    return ffi.string(charp).decode('ascii')


class Type(object):
    def __init__(self, binding, ctype):
        self.binding = binding
        self._smoke = binding.smoke.csmoke
        self._type = ctype

    @property
    def name(self):
        return pystring(self._type.name)

    @property
    def cls(self):
        if self._type.classId == -1:
            return None
        return ClassDef(CModuleIndex(self._smoke, self._type.classId))

    @property
    def valuetype(self):
        return self._type & smokec.tf_elem

    @property
    def stacktype(self):
        return {smokec.tf_stack:'stack',
                smokec.tf_ptr:'ptr',
                smokec.tf_ref:'ref'}[self._type.flags & 0x30]

    @property
    def is_const(self):
        return bool(self._type & smokec.tf_const)

    def __str__(self):
        return 'Type("%s")'%(self.name)

    __repr__ = __str__


class ClassDef(object):

    def __init__(self, binding, moduleindex):
        self.binding = binding
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        #print binding.smoke.csmoke == self._smoke, binding.smoke.csmoke, self._smoke
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
                else:
                    methods.extend(submethods)
                if not ambiguous and len(methods) > 1:
                    raise ValueError('Ambiguous method overload: %s' % name)
            return methods
        name = name.encode('ascii')
        methmnameid = smokec.Smoke_idMethodName(self._smoke, name)
        if methmnameid.index == 0:
            # No such method
            return None
        methid = smokec.Smoke_findMethodM(self._smoke, self._mi, methmnameid)
        if methid.index > 0:
            return MethodDef(self.binding,
                             CModuleIndex(methid.smoke,
                                          smokec.Smoke_methodMaps(methid.smoke)[methid.index].method))
        elif methid.index < 0:
            if ambiguous:
                aidx = -methid.index
                amethods = smokec.Smoke_ambiguousMethodList(self._smoke)
                methods = []
                while amethods[aidx] != 0:
                    methods.append(MethodDef(self.binding, amethods[aidx]))
                return methods
            else:
                raise ValueError('Ambiguous method overload: %s' % name)
        else:
            return None

    def find_munged_names(self, name):
        nameid = smokec.Smoke_idMethodName(name)
        mmaps = smokec.Smoke_methodMaps(self._smoke)
        methodnames = smokec.Smoke_methodNames(self._smoke)
        mnames = set()
        all_base_ids = set(bcls._index for bcls in self.bases)
        all_base_ids.add(self._index)
        for i in range(1, smokec.Smoke_numMethodMaps(self._smoke)):
            mmap = mmaps[i]
            if mmap.name == nameid and mmap.classId in all_base_ids:
                mname = pystring(methodnames[mmap.name])
                mnames.add(mname)
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

    def call(self, meth, inst, *args, **kwds):
        print('calling: %s::%s()' % (self.name, meth.name))
        cargs = get_args(*(args+(ffi.NULL, ffi.NULL)))
        self._classdef.classFn(meth._methoddef.method, inst if inst is not None else ffi.NULL, cargs)
        ret = cargs[0]
        if meth.is_ctor or meth.is_explicit:
            print('constructor: setting binding')
            # Constructor.
            # method index 0 is always "set smoke binding" - needed for
            # virtual method callbacks etc.
            cargs[1].s_voidp = self.binding.cbinding.binding
            self._classdef.classFn(0, ret.s_voidp, cargs)
        return ret.s_voidp

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
        return 'ClassDef(%s.%s)'%(self.binding.name, self.binding.class_name(self))

    __repr__ = __str__


class MethodDef(object):
    def __init__(self, binding, moduleindex):
        self.binding = binding
        self._mi = moduleindex
        self._smoke = moduleindex.smoke
        #assert binding.smoke.csmoke.smoke == self._smoke.smoke, (binding.smoke.csmoke.smoke, self._smoke.smoke)
        self._index = moduleindex.index
        self._methoddef = smokec.Smoke_methods(self._smoke)[self._index]
        print('meth:', self._index, pystring(smokec.Smoke_methodNames(self._smoke)[self._methoddef.name]))
        if self._methoddef.classId < 0:
            print('no class', self.name)
        else:
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
        return ret

    def call(self, inst, *args, **kwds):
        return self.cls.call(self, inst, *args, **kwds)

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

    @property
    def rettype(self):
        return Type(self._smoke, smokec.Smoke_types(self._smoke)[self._methoddef.ret])

    def __str__(self):
        return 'MethodDef(%s.%s(%s))'%(self.binding.class_name(self.cls), self.name, self.args)


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
    def __init__(self, smoke):
        self.smoke = smoke
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

    def _on_method_call(self, csmokebinding, methidx, obj, args, is_abstract):
        cmi = CModuleIndex(smokec.CSmoke_FromBinding(csmokebinding), methidx)
        meth = MethodDef(self, cmi)
        return self.method_call_handler(meth.cls, obj, meth, args, is_abstract)

    def method_call_handler(self, cls, obj, method, args, is_abstract):
        print('method_call: %s::%s()' %( cls.name, method.name))
        return 0

    def _on_class_name(self, csmokebinding, clsid):
        cmi = CModuleIndex(smokec.CSmoke_FromBinding(csmokebinding), clsid)
        cls = ClassDef(self, cmi)
        return self.class_name_handler(self, cmi)

    def class_name_handler(self, cls):
        return cls.name.replace('::', '.')

    class_name = class_name_handler

    def find_class(self, class_name):
        class_name = class_name.encode('ascii')
        return ClassDef(self, smokec.findClass(class_name))

    def iter_classes(self):
        csmoke = self.smoke.csmoke
        for i in range(1, smokec.Smoke_numClasses(csmoke)):
            cmi = CModuleIndex(csmoke, i)
            cls = ClassDef(self, cmi)
            yield cls

    def cast(self, obj, from_cls, to_cls):
        smokec.Smoke_castFn(self.smoke.smokec)(obj, from_cls, to_cls)

    def __str__(self):
        return 'Binding(%s)' % (self.name)

    __repr__ = __str__

