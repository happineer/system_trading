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
        # self.setupUi(self)  # load app screen
        self.tt_logger = TTlog()
        self.kw = Kiwoom()
        self.login()
        self.계좌수익률요청()
        # self.당일실현손익상세요청()
        # self.계좌평가현황요청()
        # self.계좌평가잔고내역요청()

    def login(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            return
        self.tt_logger.info("Login success")

    def 계좌수익률요청(self):
        screen_no = "5000"
        ret = self.kw.계좌수익률요청("계좌수익률요청", "8105566411", "5000")
        for data in ret:
            for k, v in data:
                print("{}: {}".format(k, v))
            print("-------\n\n")

        pdb.set_trace()
        print("end")

    def 당일실현손익상세요청(self):
        screen_no = "5001"
        ret = self.kw.당일실현손익상세요청("당일실현손익상세요청", "8105566411", "0000", "066570", screen_no)
        pdb.set_trace()
        for data in ret:
            for k, v in data:
                print("{}: {}".format(k, v))
            print("-------\n\n")

        pdb.set_trace()
        print("end")

    # OPW00004
    def 계좌평가현황요청(self):
        screen_no = "5002"
        account_no = "8105566411"
        account_pw = "0000"
        ret = self.kw.계좌평가현황요청("계좌평가현황요청", account_no, account_pw, "1", screen_no)
        for data in ret:
            for k, v in data:
                print("{}: {}".format(k, v))
            print("-------\n\n")

        pdb.set_trace()
        print("end")

    # OPW00018
    def 계좌평가잔고내역요청(self):
        screen_no = "5003"
        account_no = "8105566411"
        account_pw = "0000"
        ret = self.kw.계좌평가잔고내역요청("계좌평가잔고내역요청", account_no, account_pw, "1", screen_no)
        for data in ret:
            for k, v in data:
                print("{}: {}".format(k, v))
            print("-------\n\n")

        pdb.set_trace()
        print("end")


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
