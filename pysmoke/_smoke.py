
from os.path import dirname, join
import sys
import cffi

ffi = cffi.FFI()

def get_api(name):
    content = open(join(dirname(dirname(__file__)), 'include', name+'.h')).read()
    content = content[content.find('// BEGIN API'):]
    content = content[:content.find('// END API')]
    return content

smokec_api = get_api('smokec')
bindings_api = get_api('bindings')
marshal_api = get_api('marshal')

ffi.cdef('void free(void*);')
ffi.cdef(smokec_api)
ffi.cdef(bindings_api)
ffi.cdef(marshal_api)

smokec = ffi.dlopen(join(dirname(dirname(__file__)), 'smokec', 'libsmokec.so'))
bindings = ffi.dlopen(join(dirname(dirname(__file__)), 'bindings', 'libsmokebindings.so'))
marshal = ffi.dlopen(join(dirname(dirname(__file__)), 'marshal', 'libmarshalqtpy.so'))
libc = ffi.dlopen(None)

bindings.init_qtcore_CSmoke()
bindings.init_qtgui_CSmoke()


def pybytes(charp):
    return ffi.string(charp)
def pyunicode(charp):
    return ffi.string(charp).decode('utf8')

if sys.version_info[0] > 2:
    pystring = pyunicode
else:
    pystring = pybytes


