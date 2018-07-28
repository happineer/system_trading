# built-in module
import sys
import pdb
import os
import re
import time
import random
import multiprocessing
import datetime as datetime_m
from datetime import datetime
from collections import defaultdict
from collections import OrderedDict

# Data analysis
import pandas as pd

# UI(PyQt5) module
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

# Notification
from slacker import Slacker

# Database
import pymongo
from pymongo import MongoClient

# Visualization
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm

# My modules
from config import config_manager
from util.tt_logger import TTlog

# Kiwoom module
from kiwoom.kw import Kiwoom
from kiwoom.constant import KiwoomServerCheckTimeError


# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)

        # Application Configuration
        # UI
        self.setupUi(self)

        # Font(ko)
        self.set_ko_font()

        # Logger
        self.logger = TTlog(logger_name="TTRealCondi").logger

        # DB
        self.mongo = MongoClient()
        self.db = self.mongo.TopTrader

        # Slack
        self.slack = Slacker(config_manager.get_slack_token())

        # Kiwoom
        self.kw = Kiwoom()
        self.login()
        self.stock_info = self.kw.get_stock_basic_info()

        # app main
        self.main()

    def login(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            exit(-1)
        self.logger.info("Login success")

    def set_ko_font(self):
        # 그래프에서 마이너스 폰트 깨지는 문제에 대한 대처
        mpl.rcParams['axes.unicode_minus'] = False

        path = 'c:/Windows/Fonts/D2Coding-Ver1.3.2-20180524.ttf'
        font_name = fm.FontProperties(fname=path).get_name()
        plt.rcParams["font.family"] = font_name

    def main(self):
        print("Start Application")
        # 금일 급등했던 종목 정보를 가져온다.
        stock_info = self.kw.rapidly_rising_price_stock(
            market="000",
            time_gubun="2",
            time="0",
            vol_gubun="00000",
            screen_no="5000"
        )

        # 급등했던 종목중 상위 20개를 추린다.
        stock_info = stock_info[:20]

        # 상위 20개에 대해 체결강도 정보를 수집하여 DB에 저장한다.
        for stock in stock_info:
            code = stock['종목코드']
            ret = self.kw.get_chegyul_info(code, "9000")
            pdb.set_trace()
            for data in ret:
                h, m, s = data['시간'][:2], data['시간'][2:4], data['시간'][4:]
                t = datetime.today()
                data['date'] = datetime(t.year, t.month, t.day, int(h), int(m), int(s))
                data['code'] = code
                data['stock_name'] = self.stock_info[code]["stock_name"]
                data['market'] = self.stock_info[code]["market"]
            self.db.short_trading_info_chegyul.insert(ret)
            print(ret)

        # 상위 20개에 대해 분봉/틱봉 정보를 수집하여 DB에 저장한다.
        t = datetime.today()
        s_date = datetime(t.year, t.month, t.day, 9, 0, 0)
        e_date = datetime(t.year, t.month, t.day, 17, 0, 0)

        for stock in stock_info:
            code = stock['종목코드']
            ret = self.kw.stock_price_by_min(code, "1", "9001", s_date, e_date)
            for data in ret:
                data['stock_name'] = self.stock_info[code]["stock_name"]
                data['market'] = self.stock_info[code]["market"]
            self.db.time_series_min1.insert(ret)

            ret = self.kw.stock_price_by_tick(code, "10", "9002", s_date, e_date)
            for data in ret:
                data['stock_name'] = self.stock_info[code]["stock_name"]
                data['market'] = self.stock_info[code]["market"]
            self.db.time_series_tick10.insert(ret)

        # 상위 20개에 대해 호가 정보를 수집하여 DB에 저장한다.
        # for stock in stock_info:
        #     code = stock['종목코드']
        #     ret = self.kw.get_hoga_info(code, "9001")
        #     self.db.short_trading_info_hoga.insert(ret)
        #     print(ret)
        print("end")


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
