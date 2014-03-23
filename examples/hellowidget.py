#
# hellowidget.py
#
#  Created on: Nov 19, 2013
#      Author: pankaj
#

from __future__ import print_function, absolute_import

import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

from pysmoke.smoke import Args, ffi, dbg
from pysmoke.smokebindings import qtcore_smoke, qtgui_smoke, QtCore, QtGui
# Can add a higher level module for things such as
# from qtsmoke import QtCore, QtGui
# The bindings here are at a lower level.

qtcore = qtcore_smoke()
qtgui = qtgui_smoke()


def main():
    #dbg()
    qapp = QtGui.QApplication(['hello_smoke_app'])
    print('application args', QtGui.QApplication.arguments())
    #print('application name', QtGui.QApplication.applicationName())
    #print('application filepath', QtGui.QApplication.applicationFilePath())
    w = QtGui.QWidget()
    print(w.__cval__.value.s_voidp)
    b = QtGui.QPushButton('yahoo', w)
    b2 = QtGui.QLineEdit()
    b2.setParent(w)
    b2.setText('google')
    layout = QtGui.QVBoxLayout()
    layout.addWidget(b)
    layout.addWidget(b2)
    w.setLayout(layout)
    #w.setWindowTitle('Hello, Widget!!!')
    w.show()
    getattr(QtGui.QApplication, 'exec')()

if __name__ == '__main__':
    main()

