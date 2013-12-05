
import unittest

from pysmoke.smoke import ffi
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke


qtcore = qtcore_smoke()
qtgui = qtgui_smoke()
qapp = qtgui.find_class('QApplication').find_method('QApplication$?').call(
    None,
    ffi.new('int*', 1),
    ffi.new('char*[]', [ffi.new('char[]', b'test_smoke')]))

def dbg():
    from IPython.core.debugger import Tracer; Tracer()()

class SmokeTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_class(self):
        name = 'QApplication'
        cls = qtgui.find_class(name)
        self.assertEqual(cls.name, name)


class ClassDefTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_method(self):
        clsname = 'QApplication'
        cls = qtgui.find_class(clsname)
        methname = 'QApplication$?'
        meth = cls.find_method(methname)
        self.assertEqual(meth.name, 'QApplication')
        self.assertEqual(meth.cls.name, 'QApplication')

    def test_find_method_base(self):
        """ Test find_method for a base class """
        m = qtgui.find_class('QPushButton').find_method('isActiveWindow')
        self.assertTrue(m)
        self.assertEqual(m.name, 'isActiveWindow')
        self.assertEqual(m.cls.name, 'QWidget')

    def test_find_method_mod(self):
        """ Test find_method for a base class """
        methname = 'objectName'
        cls = qtgui.find_class('QPushButton')
        m = cls.find_method(methname)
        self.assertTrue(m)
        self.assertEqual(m.name, methname)
        self.assertEqual(m.cls.name, 'QObject')
        self.assertNotEqual(m.binding, cls.binding)

class MethodDefTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_call(self):
        clsname = 'QApplication'
        cls = qtgui.find_class(clsname)
        methname = 'objectName'
        meth = cls.find_method(methname)
        self.assertEqual(meth.name, methname)
        self.assertTrue(meth.call(inst=qapp))


if __name__ == '__main__':
    unittest.main()

