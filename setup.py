""" Python Qt bindings using smoke """

from setuptools import find_packages, setup
from Cython.Build import cythonize

ext_modules = cythonize("pysmoke/_smoke.pyx",
                        include_dirs = ['include'])



setup(
    name='PySmoke',
    version = '0.1',
    author = 'PySmoke Developers',
    author_email = 'pankaj86@gmail.com',
    description = "Python Qt bindings using smoke",
    long_description = __doc__,
    license = "LGPL",
    packages = find_packages(),
    ext_modules = ext_modules,
#    cmd_class = {'build_ext':build_ext},
    platforms=['Linux', 'Mac OS-X', 'Unix', 'Windows'],
    )
