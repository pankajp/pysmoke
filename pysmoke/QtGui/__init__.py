
from os.path import dirname

from pysmoke.smoke import Binding, bindings
from pysmoke.smokebindings import SmokeModule

qtgui_smoke = Binding.get_binding(bindings.qtgui_CSmoke().smoke)
QtGui = SmokeModule.get_module(qtgui_smoke, __package__)
QtGui.__path__ = [dirname(__file__)]
import sys
sys.modules[__name__] = QtGui

