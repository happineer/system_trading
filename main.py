# built-in module
import sys
import pdb
import os
import pandas as pd
import time

# UI(PyQt5) module
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

from slacker import Slacker

from kiwoom.kw import Kiwoom

# load main UI
ui = uic.loadUiType("./ui/main.ui")[0]

# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.kw = Kiwoom()
        self.kw.login()
        ret = self.kw.get_connect_state()
        pdb.set_trace()
        print("end")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tt = TopTrader()
    tt.show()
    sys.exit(app.exec_())