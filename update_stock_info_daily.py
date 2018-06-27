
# built-in module
import sys
import pdb
import os
from datetime import datetime

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
        self.kw = Kiwoom()
        self.collect_n_save_data()

    def login(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            exit(-1)
        self.tt_logger.info("Login success")

    def upsert_db(self, col, datas):
        for doc in datas:
            col.update({'date': doc['date'], 'code': doc['code']}, doc, upsert=True)

    def collect_n_save_data(self):
        self.login()
        kospi_code_list = self.kw.get_code_list_by_market(0)
        stock_list = [[c, self.kw.get_master_stock_name(c)] for c in kospi_code_list]
        stock_list = [(c, name) for c, name in stock_list if not any(map(lambda x: x in name, constant.FILTER_KEYWORD))]

        total = len(stock_list)
        for i, stock in enumerate(stock_list, 1):
            code, stock_name = stock
            print("%s/%s - %s/%s" % (i, total, code, stock_name))
            # ret = self.kw.stock_price_by_min(code, tick='1', screen_no='3000',
            #                                  begin_date=datetime(2018, 1, 1, 0, 0, 0),
            #                                  end_date=datetime(2018, 6, 25, 10, 0, 0))
            # c_time_series_min1 = self.tt_db.time_series_min1
            # c_time_series_min1.insert(ret)

            # day
            ret = self.kw.stock_price_by_day(code, screen_no='3001',
                                             begin_date=datetime(2018, 1, 1, 0, 0, 0),
                                             end_date=datetime(2018, 6, 26, 10, 0, 0))
            self.upsert_db(self.tt_db.time_series_day, ret)

            # week
            ret = self.kw.stock_price_by_week(code, screen_no='3002',
                                             begin_date=datetime(2018, 1, 1, 0, 0, 0),
                                             end_date=datetime(2018, 6, 26, 10, 0, 0))
            self.upsert_db(self.tt_db.time_series_week, ret)

            # month
            ret = self.kw.stock_price_by_month(code, screen_no='3003',
                                              begin_date=datetime(2018, 1, 1, 0, 0, 0),
                                              end_date=datetime(2018, 6, 26, 10, 0, 0))
            self.upsert_db(self.tt_db.time_series_month, ret)


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
