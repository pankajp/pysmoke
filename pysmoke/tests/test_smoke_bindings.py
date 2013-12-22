from __future__ import print_function, absolute_import

import unittest

from pysmoke.smoke import ffi, Type, TypedValue
from pysmoke.smokebindings import QtCore, QtGui

QApplication = QtGui.QApplication

print('QApplication:', QApplication, QApplication.__bases__, QApplication.__mro__, QApplication.QApplication, QtCore.QCoreApplication.QCoreApplication, 'foo')

qtgui = QtGui.__binding__

def dbg():
    from IPython.core.debugger import Tracer; Tracer()()

#dbg()
qapp = QtGui.QApplication(['foo'])

def pm(meth):
    print(meth, meth.cls._classdef, meth._methoddef, meth.binding, meth.cls.binding)

class SmokeTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instance(self):
        print('qapp cls', QApplication)
        #dbg()
        inst = QApplication.instance()
        qinstm = qtgui.find_class('QCoreApplication').find_method('instance')
        print(qinstm)
        qinst = qinstm.call(None)
        print('chk', qapp, inst, qinst, QApplication.instance)
        #self.assertEqual(inst, qapp)
        #dbg()
        qaname = qapp.objectName()
        self.assertEqual(qaname, u'foo')


if __name__ == '__main__':
    unittest.main()

