
from os.path import dirname, join
import cffi

ffi = cffi.FFI()

def get_api(content):
    content = content[content.find('// BEGIN API'):]
    content = content[:content.find('// END API')]
    return content

smokec_api = get_api(open('include/smokec.h').read())
bindings_api = get_api(open('include/bindings.h').read())


ffi.cdef(smokec_api)
ffi.cdef(bindings_api)
smokec = ffi.dlopen(join(dirname(dirname(__file__)), 'smokec', 'libsmokec.so'))
bindings = ffi.dlopen(join(dirname(dirname(__file__)), 'bindings', 'libsmokebindings.so'))

bindings.init_qtcore_CSmoke()
bindings.init_qtgui_CSmoke()
