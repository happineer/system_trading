# built-in module
import sys
import pdb
import os
from datetime import datetime
from datetime import timedelta

import pandas as pd
import time
from database.db_manager import DBM

# UI(PyQt5) module
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

from kiwoom.kw import Kiwoom
from config import config_manager
from util.tt_logger import TTlog
from util.slack import Slack

from database.db_manager import DBM
from pymongo import MongoClient
import pymongo
import random
from collections import defaultdict
from kiwoom.constant import KiwoomServerCheckTimeError
import multiprocessing
from util import constant

# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.logger = TTlog().logger
        self.slack = Slack(config_manager.get_slack_token())
        self.dbm = DBM('TopTrader')
        self.main()

    def complete_tick_data(self, date):
        return self.dbm.get_collect_tick_data_status(date, tick="1") == "END"

    def main(self):
        date = datetime(2018, 8, 2)
        with open("base_date_when_collect_tick_data.txt", "w") as f:
            f.write("{} {} {}\n".format(date.year, date.month, date.day))

        while not self.complete_tick_data(date):
            os.system("python collect_1tick_data_real_condi_search.py")


# Print Exception Setting
sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook

if __name__ == "__main__":
    global app
    app = QApplication(sys.argv)
    tt = TopTrader()
    tt.show()
    sys.exit(app.exec_())
