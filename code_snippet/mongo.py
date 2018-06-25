
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

        self.test()

    def test(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            return
        self.tt_logger.info("Login success")

        code_list = self.kw.get_code_list_by_market(0)
        # except keyword
        stock_list = [[c, self.kw.get_master_stock_name(c)] for c in code_list]
        stock_list = [(c, name) for c, name in stock_list if not any(map(lambda x: x in name, constant.stock_filter))]

        total = len([])
        pdb.set_trace()
        # for i, stock in enumerate(stock_list, 1):
        for i, stock in enumerate(stock_list[:20], 1):
            code, stock_name = stock
            print("%s/%s" % (i, total))
            stock_name = self.kw.get_master_stock_name(code)
            data = self.kw.stock_price_by_min(code, tick='1')  # 1분봉 데이터
            [d.update({"code": code, "stock_name": stock_name, "market": "kospi"}) for d in data]
            data = sorted(data, key=lambda x: x.get("date"), reverse=True)
            col = self.tt_db.min1_trend
            last_one = col.find({"code": code}).sort('date', pymongo.DESCENDING).limit(1)

            if last_one.count() != 0:
                last_datetime = last_one.next().get('date')
                data = [d for d in data if d.get("date") > last_datetime]

            if bool(data):
                col.insert(data)
                print("[%s] Insert Data Completed! (1min)" % stock_name)
            else:
                print("[%s] There is no data to insert DB" % stock_name)

            # random delay
            if i % 5 == 0:
                delay_time = random.choice(range(5, 10))
                print("Delay Time: %s" % delay_time)
                time.sleep(delay_time)
        print("Store Stock data to db. Completed !")
        pdb.set_trace()

        col = self.tt_db.day_trend
        ret = col.find().sort({"일자": -1}).limit(1)
        pdb.set_trace()
        data = self.kw.stock_price_by_day('207940', date='20180615')  # 삼바
        [d.update({"code": "207940"}) for d in data]
        col = self.tt_db.day_trend
        col.insert(data)
        print("Insert Data Completed! (day)")
        pdb.set_trace()

        col = self.tt_db.week_trend
        data = self.kw.stock_price_by_week('207940', s_date='20180611', e_date='20180615')  # 삼바
        [d.update({"code": "207940"}) for d in data]
        col = self.tt_db.week_trend
        col.insert(data)
        print("Insert Data Completed! (week)")
        pdb.set_trace()

        data = self.kw.stock_price_by_month('207940', s_date='20180611', e_date='20180615')  # 삼바
        [d.update({"code": "207940"}) for d in data]
        col = self.tt_db.month_trend
        col.insert(data)
        print("Insert Data Completed! (month)")
        pdb.set_trace()


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
