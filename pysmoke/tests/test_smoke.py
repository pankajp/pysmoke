from __future__ import print_function, absolute_import

import random
import unittest

from pysmoke.smoke import ffi, Type, TypedValue, pystring, smokec, not_implemented, charp, dbg
from pysmoke import QtCore, QtGui

qtcore = QtCore.__binding__
qtgui = QtGui.__binding__
arg = ['foo']
qapp = QtGui.QApplication(arg)



qinst = qtgui.find_class('QCoreApplication').find_method('instance').call(None)

print(qapp, qinst)




class TypeTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_smoke_type(self, idx, binding):
        ctyp = smokec.Smoke_types(binding.smoke.csmoke)[idx]
        typ = Type(binding, ctyp)
        return typ

    def iter_rand_types(self, count=100):
        for binding in (qtcore, qtgui):
            num_types = smokec.Smoke_numTypes(binding.smoke.csmoke)
            for i in range(count):
                yield self.get_smoke_type(random.randrange(0, num_types),
                                          binding)

    def iter_all_types(self):
        for binding in (qtcore, qtgui):
            for typ in Type.iter_types(binding):
                yield typ

    def test_name(self):
        for typ in self.iter_all_types():
            if typ.name == '':
                print('skipping %s(%s): empty name' % (typ, typ._type.flags))
                continue
            self.assertEqual(typ.name, pystring(typ._type.name), typ)

    def _assert_cls_name_equal(self, typ, cls):
        if typ._type.classId == 0:
            self.assertIsNone(cls, typ)
        elif typ.cls is None:
            # FIXME: enum classes not implemented
            self.assertEqual(typ.type_id_name, 't_enum')
        else:
            cls_name = cls.name
            if cls.name == 'QGlobalSpace':
                # FIXME:
                print('skipping %s: QtGlobal declarations not implemented' % (
                    typ))
                return
            if typ.type_id_name == 't_enum':
                # FIXME:
                print('skipping %s: enums not implemented' % (
                    typ))
                return
            if '::' in typ.name:
                # FIXME:
                print('skipping %s: nested classes not implemented' % (
                    typ))
                return
            if typ.is_const:
                cls_name = 'const ' + cls_name
            # startswith to account for reference or pointer types
            self.assertTrue(typ.name.startswith(cls_name),
                                '%s, %s, %s, %s' % (
                                    typ, cls, typ.name, cls_name))

    def _assert_typ_equal(self, typ1, typ2):
        try:
            if '::' in typ1.name:
                not_implemented('nested classes')
                return
            self.assertEqual(typ1.type_id, typ2.type_id)
            self.assertEqual(typ1.type_id, typ1._type.flags & smokec.tf_elem)
            self.assertEqual(typ1.type_id_name, typ2.type_id_name)
            self.assertEqual(typ1.stackitem_name, typ2.stackitem_name)
            self.assertEqual('t'+typ1.stackitem_name[1:],
                            typ1.type_id_name)
            # ref can become ptr
            #self.assertEqual(typ1.stacktype, typ2.stacktype)
            # constness is lost in translation
            #self.assertEqual(typ1.is_const, typ2.is_const)
            self.assertEqual(typ1.stackitem_name, typ2.stackitem_name)
        except Exception as e:
            print(typ1, typ2)
            dbg()
            raise

    def _create_ctype(self, name, elem, stack, is_const, classid=0):
        ctype = ffi.new('Type*')
        self._nam = charp(name)
        ctype.name = self._nam
        ctype.classId = classid
        ctype.flags = getattr(smokec, elem)
        ctype.flags |= getattr(smokec, 'tf_'+stack)
        ctype.flags |= smokec.tf_const if is_const else 0
        return ctype

    def test_typ_props(self):
        for name in ('foo_bar', 'foo::baz'):
            for elem_val, elem_name in Type._type_id_map.items():
                if elem_name == 'tf_last':
                    # This is just to indicate end of values
                    continue
                for stack in 'stack', 'ref', 'ptr':
                    for is_const in (True, False):
                        ctyp = self._create_ctype(name, elem_name, stack, is_const)
                        typ = Type(qtcore, ctyp)
                        self.assertEqual(typ.name, name)
                        self.assertEqual(typ.cls, None)
                        self.assertEqual(typ.type_id, elem_val)
                        self.assertEqual(typ.type_id_name, elem_name)
                        self.assertEqual(typ.stackitem_name, 's'+elem_name[1:])
                        self.assertEqual(typ.stacktype, stack)
                        self.assertEqual(typ.is_const, is_const)

    def test_cls(self):
        for typ in self.iter_all_types():
            self._assert_cls_name_equal(typ, typ.cls)
            if typ.cls is None:
                continue
            # check roundtrip from typ->cls->typ
            cls = typ.cls
            typ2 = Type.from_cls(cls)
            self._assert_typ_equal(typ, typ2)

    def test_from_cls(self):
        for binding in (qtcore, qtgui):
            for cls in binding.iter_classes():
                typ = Type.from_cls(cls)
                self._assert_cls_name_equal(typ, cls)


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

    def test_find_method_by_args(self):
        """ Find method using specified args """
        methname = 'disconnect'
        cls = qtgui.find_class('QObject')
        #dbg()
        args = []
        m = cls.find_method_by_args(methname, args)
        self.assertTrue(m)
        self.assertEqual(m.name, methname)
        self.assertEqual(m.cls.name, 'QObject')
        self.assertEqual(len(m.args), len(args))
        #self.assertNotEqual(m.binding, cls.binding)

        methname = 'disconnect'
        cls = qtgui.find_class('QObject')
        #dbg()
        args = ['foo']
        m = cls.find_method_by_args(methname, args)
        self.assertTrue(m)
        self.assertEqual(m.name, methname)
        self.assertEqual(m.cls.name, 'QObject')
        self.assertEqual(len(m.args), len(args))
        #self.assertNotEqual(m.binding, cls.binding)


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
        self.assertEqual(meth.cls.name, 'QObject')
        print('qapp_name', qapp.objectName())
        self.assertTrue(meth.call(inst=qapp.__cval__.value.s_voidp))

    def test_object_addr(self):
        import gc
        objs = []
        ids = []
        for i in range(10):
            obj = QtCore.QObject()
            id = obj.__cval__.value.s_long
            objs.append(obj)
            ids.append(id)
            QtCore.QObject()
            gc.collect()
        gc.collect()
        self.assertListEqual(ids, [o.__cval__.value.s_long for o in objs])

if __name__ == '__main__':
    unittest.main()

