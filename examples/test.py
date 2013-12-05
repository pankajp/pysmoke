from __future__ import print_function

import sys, os
from os.path import join, dirname
sys.path.append(dirname(dirname(__file__)))

from pysmoke import smoke, smokebindings
from pysmoke.smoke import Args, ffi, pystring

from pysmoke.smokebindings import qtgui_smoke


qtgui = qtgui_smoke()
for c in qtgui.iter_classes():
    if c._classdef.className:
        print(c.name, c._classdef.parents, c._classdef.external, c._classdef.flags, c._classdef.size)
    else:
        print(c._index)
c = qtgui.find_class('QPushButton')
m = c.find_method('QWidget')
print(m.name)
print(m.args)

for meth in c.iter_methods():
    print(meth)

print('finding a meth')
rm = c.find_method('render#')
print(c.find_method('render#'))

print('render methods')
mn = 'render'
print(c.find_munged_names(mn))

print('finding render')
for meth in c.find_method(mn, munged=False):
    print(meth)

print('checking for render in all methods')
for meth in c.iter_methods():
    if meth.name.startswith(mn):
        print('render found', meth)
        break
    elif meth.name.startswith('r'):
        print(meth)
else:
    print('render not found')

print(smoke.smokec.Smoke_numClasses(qtgui.smoke.csmoke))
print(smoke.smokec.Smoke_numMethodNames(qtgui.smoke.csmoke))
print(smoke.smokec.Smoke_numMethods(qtgui.smoke.csmoke))
print(smoke.smokec.Smoke_numMethodMaps(qtgui.smoke.csmoke))

print(qtgui.find_class('QWidget').find_munged_names(mn))

qapp_cls = qtgui.find_class('QApplication')
print(qapp_cls.name, qapp_cls)
qapp_ctor = qapp_cls.find_method('QApplication$?')
for meth in qapp_cls.iter_methods():
    print(meth, meth._index, meth._smoke.smoke)
print(qapp_ctor.name, qapp_ctor, qapp_ctor._index)
print(qapp_ctor._class.name)

args = Args(3)
argn = ffi.new('int[1]', [2])
args[1].s_voidp = argn
argv = ffi.new('char[]', b'hello_smoke_app')
argc = ffi.new('char*[]', [argv, argv])
args[2].s_voidp = argc
qapp = qapp_ctor.call(None, argn, argc)

qcapp = qtgui.find_class('QCoreApplication')
qcinst = qcapp.find_method('instance').call(inst=None)
print(qcapp, qcinst, qcapp.find_method('objectName'))
print(qcapp.find_method('objectName').call(inst=qcinst))
m = qapp_cls.find_method('objectName')
print(m)
print(m.cls, m.cls.bases, m.cls.is_external)
print(m.call(inst=qapp))

qw = qtgui.find_class('QWidget')
qw.find_method('objectName')
