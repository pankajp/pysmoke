PySmoke
-------

.. image:: https://travis-ci.org/pankajp/pysmoke.svg?branch=master
   :target: https://travis-ci.org/pankajp/pysmoke

This project is a python binding to the Smoke library, which is a C++
library to make it simpler to create bindings for C++ libraries
in other languages. Smoke is developed by KDE developers and
currently is used in KDE to generate bindings fo Qt and KDE libraries
in various languages such as perl, ruby, lisp etc.

The PySmoke project aims to provide a python for smoke library
and also a C API for the same so that it is simpler to interface
directlty with other languages which provide a C API without having
to write C++ code.

The initial goal of the PySmoke project is to generate python
bindings for qt using smoke, which reside in the pysmoke python
package.


Installation
------------

Prerequisites
~~~~~~~~~~~~~

PySmoke depends on Qt and smoke as runtime dependencies, along
with the cffi python package.
The build process also needs setuptools, cmake and a decent C++ compiler.

Installing
~~~~~~~~~~

Currently, only in-tree development installation is supported::

   cmake .
   make
   python setup.py develop

In future we may improve the installation process to be more flexible
and provide binary eggs for various platforms.


Contributing
------------

We welcome all contributions into the project, from bug reports
feature requests to documentation, code and build scripts.


TODO
----

The following are major areas of work remaining:

- Binding Signals-Slots and Properties

- Binding enums, nested classes and namespaces

- Binding operators (<,>,==,iteration etc)

- Binding thngs not implemented in Smoke (QString like classes, templates)

- Qt5 strategy

- Fixing issues w/ pypy (segfaults)

- Figure out memory management

- More examples, documentation and tests

- Better build support

- Compatibility with PySide/PyQt4 code out there


License
-------

The contents of this project are licensed under the terms of the
MIT License found in the file COPYING at the root of the project
and also at http://opensource.org/licenses/MIT
