SmokeC
------

This project is a C binding to the Smoke library, which is a C++
library to make it simpler to create bindings for C++ libraries
in other languages. Smoke is developed by KDE developers and
currently is used in KDE to generate bindings fo Qt and KDE libraries
in various languages such as perl, ruby, lisp etc.

The SmokeC project aims to provide a C API for smoke library so
that it is simpler to interface directlty with other languages
which provide a C API without having to write C++ code.

For example, it should be possible to directly use this library from
python via ctypes or CFFI without having to write separate C++ shim
to bridge the smoke C++ API with python's C API.

License
-------

Undefined: Currently the licensing terms have not yet been decided.
