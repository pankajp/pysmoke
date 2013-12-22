from __future__ import print_function, absolute_import


from pysmoke.smoke import Args, ffi
from pysmoke.smokebindings import SmokeClass, SmokeMetaClass, QtGui, QtCore


class QApplication(SmokeMetaClass.get_class('QCoreApplication',
                                            QtCore.__binding__)):

    def __init__(self, argv):
        print('QA args', argv)
        args = Args(3)
        argn = ffi.new('int[1]', [len(argv)])
        args[1].s_voidp = argn
        argv = [ffi.new('char[]', arg.encode('ascii')) for arg in argv]
        argc = ffi.new('char*[]', argv)
        args[2].s_voidp = argc
        super(QApplication, self).__init__(argn, argc)
