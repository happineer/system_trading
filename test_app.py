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
from database.db_manager import DBM

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
        self.dbm = DBM('TopTrader')

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

        path = 'c:/Windows/Fonts/D2Coding-Ver1.3-20171129.ttc'
        font_name = fm.FontProperties(fname=path).get_name()
        plt.rcParams["font.family"] = font_name

    def main(self):
        print("Start Application")
        target_date = datetime(2018, 8, 2)
        y, m, d = target_date.year, target_date.month, target_date.day
        s_time = datetime(y, m, d, 9, 0, 0)
        e_time = datetime(y, m, d, 15, 30, 0)
        self.code = '000020'
        df = pd.DataFrame(self.dbm.get_tick_data(self.code, target_date, tick="1"))
        ts_group = df.groupby('timestamp')
        volumn = pd.DataFrame(ts_group.sum()['거래량'])
        price = pd.DataFrame(ts_group.max()['현재가'])
        index = pd.date_range(s_time, e_time, freq='S')
        volumn = volumn.reindex(index, method='ffill', fill_value=0)
        price = price.reindex(index, method='ffill', fill_value=0)
        price['volumn'] = volumn

        from trading.account import Stock

        tick_data = defaultdict(list)
        stock_list = [Stock('900100', '주식1'), Stock('200710', '주식2'), Stock('206560', '주식3')]
        for stock in stock_list:
            stock.gen_time_series_sec1(target_date)
            tick_data[stock.code] = stock.time_series_sec1
        pdb.set_trace()

        db_data = self.dbm.get_real_condi_search_data(target_date, "소형주_급등_005_003")

        condi_hist = defaultdict(defaultdict)
        for data in db_data[:5]:
            code, date = data['code'], data['date'].replace(microsecond=0)
            price = tick_data[code].ix[date]['현재가']
            condi_hist[code][date] = price

        pdb.set_trace()
        print("End Application")


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
