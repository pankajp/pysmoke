#
# hellowidget.py
#
#  Created on: Nov 19, 2013
#      Author: pankaj
#

from __future__ import print_function, absolute_import

import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

from pysmoke.smoke import Args, ffi
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke
# Can add a higher level module for things such as
# from qtsmoke import QtCore, QtGui
# The bindings here are at a lower level.

qtcore = qtcore_smoke()
qtgui = qtgui_smoke()


def main():
    qapp_cls = qtgui.find_class('QApplication')
    print(qapp_cls.name, qapp_cls)
    qapp_ctor = qapp_cls.find_method('QApplication$?')
    print(qapp_ctor.name, qapp_ctor)
    print(qapp_ctor._class.name)

    args = Args(3)
    argn = ffi.new('int[1]', [2])
    args[1].s_voidp = argn
    argv = ffi.new('char[]', b'hello_smoke_app')
    argc = ffi.new('char*[]', [argv, argv])
    args[2].s_voidp = argc
    qapp = qapp_ctor.call(None, argn, argc)

    qwidget_cls = qtgui.find_class('QWidget')
    qwidget_ctor = qwidget_cls.find_method('QWidget')
    qwidget = qwidget_ctor.call(None)
    qwidget_cls.find_method('show').call(qwidget)
    qapp_cls.find_method('exec').call(qapp)


if __name__ == '__main__':
    main()

