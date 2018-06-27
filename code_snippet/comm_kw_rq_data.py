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
        self.kw = Kiwoom()
        self.login()

        self.test()

    def login(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            return
        self.tt_logger.info("Login success")

        self.set_account()

    def set_account(self):
        print("request account number")
        ret = self.kw.get_login_info("ACCNO")
        self.account_no = ret.strip(";").split(";")[0]

    def test(self):
        print("관심종목조회!")
        code_list = '066570;207940'
        ret = self.kw.get_stock_infos(code_list, '6000', 0, 0)
        print("관심종목조회 요청!")


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
