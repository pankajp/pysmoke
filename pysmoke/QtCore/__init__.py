
from os.path import dirname

from pysmoke.smoke import Binding, bindings
from pysmoke.smokebindings import SmokeModule

qtcore_smoke = Binding.get_binding(bindings.qtcore_CSmoke().smoke)
QtCore = SmokeModule.get_module(qtcore_smoke, __package__)
QtCore.__path__ = [dirname(__file__)]


QtCore.SLOT = lambda signature: '1' + signature
QtCore.SIGNAL = lambda signature: '2' + signature


import sys
sys.modules[__name__] = QtCore

