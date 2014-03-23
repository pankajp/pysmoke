""" Python Qt bindings using smoke """

from setuptools import find_packages, setup


setup(
    name = 'PySmoke',
    version = '0.1',
    author = 'PySmoke Developers',
    description = "Python Qt bindings using smoke",
    long_description = __doc__,
    license = "LGPL",
    packages = find_packages(),
    zip_safe = False,
    platforms = ['Linux', 'Mac OS-X', 'Unix', 'Windows'],
    )
