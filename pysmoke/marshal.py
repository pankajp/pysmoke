
from _smoke import marshal, pyunicode, ffi, libc


class QString(object):
    @classmethod
    def to_py(cls, obj):
        charp = marshal.QString_to_utf8(obj)
        ret = pyunicode(charp)
        libc.free(charp)
        return ret

    @classmethod
    def from_py(cls, obj):
        if isinstance(obj, unicode):
            obj = obj.encode('utf8')
        charp = ffi.new('char[]', obj)
        return marshal.QString_from_utf8(charp)


if __name__ == '__main__':
    print QString.from_py(u'yahoo')
    print QString.from_py(b'yahoo')

