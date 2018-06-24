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

        stock_data = defaultdict(dict)
        c_stock_info = self.tt_db.stock_info
        c_theme_info = self.tt_db.theme_info

        code_list = self.kw.get_code_list_by_market(0)
        code_list = [c for c in code_list if c_stock_info.find({"code": c}).count() == 0]
        total = len(code_list)
        for i, code in enumerate(code_list[:5], 1):
            print("%s/%s" % (i, total))
            stock_name = self.kw.get_master_stock_name(code)
            print("New Stock Code Found ! -> %s, %s" % (code, stock_name))
            stock_data[code] = {
                "code": code,
                "stock_name": stock_name,
                "market": "kospi"
            }
            time.sleep(0.5)

        theme_grp_list = self.kw.get_theme_group_list(0)
        theme_grp_list = [(tc, tn) for tc, tn in theme_grp_list if c_theme_info.find({"theme_code": tc}).count() == 0]
        theme_data = {}
        total = len(theme_grp_list)
        for i, ti in enumerate(theme_grp_list, 1):
            print("%s/%s" % (i, total))
            theme_code, theme_name = ti
            print("Theme_code: %s, Theme_name: %s" % (theme_code, theme_name))

            code_list = [c[1:] for c in self.kw.get_theme_group_code_list(theme_code)]
            for code in code_list:
                stock_data[code].setdefault("theme_code", []).append(theme_code)
                stock_data[code].setdefault("theme_name", []).append(theme_name)
                stock_data[code]["code"] = code
                stock_data[code]["market"] = "kospi"
                if "stock_name" not in stock_data[code]:
                    stock_data[code]["stock_name"] = self.kw.get_master_stock_name(code)

            theme_data[theme_code] = {
                "theme_code": theme_code,
                "theme_name": theme_name,
                "stock_list": [stock_data[c] for c in code_list]
            }
            time.sleep(0.5)

        pdb.set_trace()
        # save stock_info
        stored_code_list = [s["code"] for s in c_stock_info.find()]
        new_data = [v for k, v in stock_data.items() if k not in stored_code_list]
        if bool(new_data):
            c_stock_info.insert(new_data)

        pdb.set_trace()
        # save theme_info
        stored_theme_list = [t["theme_code"] for t in c_theme_info.find()]
        new_data = [v for k, v in theme_data.items() if k not in stored_theme_list]
        if bool(new_data):
            c_theme_info.insert(new_data)
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
