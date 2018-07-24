# built-in module
import sys
import pdb
import os
import pandas as pd
import time

# UI(PyQt5) module
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
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
        self.logger = TTlog().logger
        self.db = MongoClient().TopTrader
        self.kw = Kiwoom()
        self.login()
        self.realtime_stream()
        self.timer = None
        self.start_timer()

    def login(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            return
        self.logger.info("Login success")

    def start_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_call)
        # self.timer.setSingleShot(True)
        self.timer.start(10000) # 10 sec interval

    def timer_call(self):
        self.logger.info("")
        self.logger.info("="* 100)
        self.logger.info("Timer Call !")
        self.logger.info("=" * 100)

    def realtime_stream_callback(self, data):
        self.logger.info("[realtime_stream_callback]")
        self.logger.info("data: {}".format(data))
        self.db.realtime_stream.insert({'real_data': data})

    def realtime_stream(self):
        code_list = "066570;000030;000270;000660;005930;068270;045390;064350;011390;025560"
        screen_no = "6001"
        self.kw.reg_callback("OnReceiveRealData", "", self.realtime_stream_callback)
        self.kw.set_real_reg(screen_no, code_list, "10;11;12;13;14;16;17;27;28;", 0)


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

