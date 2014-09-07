from __future__ import print_function, absolute_import


from pysmoke.smoke import Args, ffi
from pysmoke.smokebindings import SmokeClass, SmokeMetaClass
from .. import QtGui


class QApplication(SmokeMetaClass.get_class('QApplication',
                                            QtGui.__binding__)):

    def __init__(self, argv):
        print('QA args', argv)
        args = Args(3)
        argn = ffi.new('int[1]', [len(argv)])
        args[1].s_voidp = argn
        self._cargn = argn
        self._args = [arg.encode('ascii') for arg in argv]
        self._cargs = [ffi.new('char[]', arg) for arg in self._args]
        self._cargv = ffi.new('char *[]', self._cargs)
        args[2].s_voidp = self._cargv
        self.__cval__ = self.__classdef__.call(self.__classdef__.name, None, [argn, self._cargv], {})
        type(self)._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

