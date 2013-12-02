#
# hellowidget.py
#
#  Created on: Nov 19, 2013
#      Author: pankaj
#

from pysmoke import smoke
from pysmoke.smoke import Smoke, Binding, smokec, bindings, delete_callback, method_call_handler, class_name_handler, Args, ffi
from pysmoke import smokebindings
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke
# Can add a higher level module for things such as
# from qtsmoke import QtCore, QtGui
# The bindings here are at a lower level.

core_smoke = bindings.qtcore_CSmoke()
gui_smoke = bindings.qtgui_CSmoke()

@delete_callback
def on_deleted(binding, obj):
    print "~%s (%s)" % (type(obj).__name__, obj)
    return ffi.new('int', 0)
    return 0

@method_call_handler
def on_method_call(binding, method, obj, args, is_abstract=False):
    s = ''
    smoke = smokec.CSmoke_FromBinding(binding)
    meth = smokec.Smoke_methods(smoke)[method]
    if meth.flags & smokec.mf_protected:
        s += 'protected '
    if meth.flags & smokec.mf_const:
        s += 'const '
    s += ffi.string(smokec.Smoke_methodNames(smoke)[meth.name])
    s += '('
    idx = smokec.Smoke_argumentList(smoke) + meth.args
    while idx[0]:
        s += ffi.string(smokec.Smoke_types(smoke)[idx[0]].name)
        idx += 1
        if idx[0]:
            s += ', '
    s += ')'
    print '%s(%s)::%s' % (ffi.string(smokec.SmokeBinding_className(binding, meth.classId)), obj, s)
    return 0

@class_name_handler
def on_class_name(binding, class_):
    name = smokec.Smoke_classes(smokec.CSmoke_FromBinding(binding))[class_].className
    return name

core_binding = smokec.SmokeBinding_new(core_smoke, on_deleted, on_method_call, on_class_name)
gui_binding = smokec.SmokeBinding_new(gui_smoke, on_deleted, on_method_call, on_class_name)


def get_class(name):
    clsid = smokec.findClass(name)
    cls = smokec.Smoke_classes(clsid.smoke)[clsid.index]
    return clsid, cls

def get_method(cls, name):
    clsid, _cls = get_class(cls)
    methid = smokec.Smoke_findMethod(clsid.smoke, cls, name)
    if methid <= 0:
        print 'get_method exc:', cls, name, methid
    meth = smokec.Smoke_methods(methid.smoke)[smokec.Smoke_methodMaps(methid.smoke)[methid.index].method]
    return methid, meth

def get_args(*args):
    cargs = Args(len(args)+1)
    for i,arg in enumerate(args):
        cargs[i+1].s_voidp = arg
    return cargs

def call(cls, meth, args=[], inst=None):
    """
    If inst is None (default): the method is assumed to be a constructor
    and the binding for the returned object is set automatically.
    For static methods which do not need an inst and do not have to set
    the binding, use inst=0
    args is a list of args which can be cast to (void*)
    """
    _, _cls = get_class(cls)
    _methid, _meth = get_method(cls, meth)
    print 'calling cls:', ffi.string(_cls.className), _cls.external, _cls.parents, _cls.classFn, _cls.enumFn, _cls.flags, _cls.size
    print 'calling:',  _meth.classId, _meth.name, _meth.args, _meth.numArgs, _meth.flags, _meth.ret, _meth.method
    cargs = get_args(*(args+[ffi.NULL, ffi.NULL]))
    _cls.classFn(_meth.method, inst if inst is not None else ffi.NULL, cargs)
    ret = cargs[0]
    if inst is None:
        # Constructor?
        # FIXME: what about static class methods?
        # method index 0 is always "set smoke binding" - needed for
        # virtual method callbacks etc.
        cargs[1].s_voidp = gui_binding.binding
        _cls.classFn(0, ret.s_voidp, cargs)
    return ret.s_voidp

def main():
    args = Args(3)
    argn = ffi.new('int[1]', [2])
    args[1].s_voidp = argn
    argv = ffi.new('char[]', 'my_smoke_app')
    argc = ffi.new('char*[]', [argv, argv])
    args[2].s_voidp = argc
    qapp = call('QApplication', 'QApplication$?', [argn, argc])

    qwidget = call('QWidget', 'QWidget')
    call('QWidget', 'show', args=[], inst=qwidget)

    call('QApplication', 'exec', inst=qapp)


if __name__ == '__main__':
    main()

