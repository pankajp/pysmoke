from __future__ import absolute_import, print_function

from ._smoke import marshal, pyunicode, ffi, libc

try:
    unicode
except NameError:
    unicode = str


class TypeConverter(object):
    """ Abstract interface for Type converters to/from C.
    objects recv/sent from c are of specified value as in `TypeId`
    """
    @classmethod
    def to_py(cls, obj):
        """ convert to py; obj is a item of specified type, or something
        """

    @classmethod
    def from_py(cls, obj):
        """ Return a pointer to specific type.
        """

    @classmethod
    def is_compatible(cls, obj):
        """ Return whether the given pyobj can be converted to type.
        """
        return False


class QString(object):
    @classmethod
    def to_py(cls, obj):
        ptr = obj
        if ffi.typeof(obj) in [ffi.typeof('StackItem*'),
                               ffi.typeof('StackItem[]'),
                               ffi.typeof('union StackItem')]:
            ptr = obj.s_voidp
        if ptr == ffi.NULL:
            print('null string received')
            return ''
        charp = marshal.QString_to_utf8(ptr)
        ret = pyunicode(charp)
        libc.free(charp)
        return ret

    @classmethod
    def from_py(cls, obj):
        if isinstance(obj, unicode):
            obj = obj.encode('utf8')
        charp = ffi.new('char[]', obj)
        return marshal.QString_from_utf8(charp)

    @classmethod
    def is_compatible(cls, obj):
        if isinstance(obj, (unicode, bytes)):
            return True


int_type = int

class int(object):
    @classmethod
    def to_py(cls, obj):
        return int_type(obj)

    @classmethod
    def from_py(cls, obj):
        if isinstance(obj, ffi.CData):
            return obj
        return ffi.new('int*', obj)

    @classmethod
    def is_compatible(cls, obj):
        try:
            cls.to_py(obj)
        except Exception:
            return False
        else:
            return True


if __name__ == '__main__':
    print(QString.from_py(u'yahoo'))
    print(QString.from_py(b'yahoo'))

