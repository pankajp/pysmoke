from .smoke import Smoke, Binding, smokec, bindings



def qtcore_smoke():
    return Binding(Smoke(bindings.qtcore_CSmoke()))


def qtgui_smoke():
    return Binding(Smoke(bindings.qtgui_CSmoke()))

