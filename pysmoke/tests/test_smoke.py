
import unittest

from pysmoke.smoke import ffi
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke


qtcore = qtcore_smoke()
qtgui = qtgui_smoke()
qapp = qtgui.find_class('QApplication').find_method('QApplication$?').call(
    None,
    ffi.new('int*', 1),
    ffi.new('char*[]', [ffi.new('char[]', 'test_smoke')]))


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



class MethodDefTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_call(self):
        clsname = 'QApplication'
        cls = qtgui.find_class(clsname)
        methname = 'QApplication$?'
        meth = cls.find_method(methname)
        self.assertEqual(meth.name, 'QApplication')


if __name__ == '__main__':
    unittest.main()

