
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
from kiwoom import constant
from config import config_manager
from util.tt_logger import TTlog

from database.db_manager import DBM
from pymongo import MongoClient
import pymongo
import random
from collections import defaultdict

# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # load app screen
        self.tt_logger = TTlog()
        self.dbm = DBM()

        self.mongo = MongoClient()
        self.tt_db = self.mongo.TopTrader
        self.slack = Slacker(config_manager.SLACK_TOKEN)
        self.kw = Kiwoom()

        self.algo_trading()

    def algo_trading(self):
        pass


# Print Exception Setting
sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tt = TopTrader()
    tt.show()
    sys.exit(app.exec_())
