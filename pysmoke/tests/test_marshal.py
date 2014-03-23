from __future__ import print_function, absolute_import

import random
import unittest

from pysmoke import marshal
from pysmoke.smoke import ffi, Type, TypedValue, pystring, smokec, not_implemented, charp, dbg
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke, QtCore, QtGui


qtcore = qtcore_smoke()
qtgui = qtgui_smoke()


class MarshalTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_qstring(self):
        qstr = marshal.QString.from_py('aqstring')
        print(qstr)
        pstr = marshal.QString.to_py(qstr)
        #dbg()
        self.assertEqual(pstr, 'aqstring')
        import gc; gc.collect()
        qstr2 = marshal.QString.from_py(pstr)
        print('QS:', qstr, pstr, qstr2, marshal.QString.to_py(qstr))

        obj = QtGui.QObject()
        print('obj', obj.__cval__.value.s_voidp)
        obj.setObjectName('my_object')
        self.assertEqual(obj.objectName(), 'my_object')

if __name__ == '__main__':
    unittest.main()

