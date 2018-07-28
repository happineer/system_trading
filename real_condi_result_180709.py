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
from kiwoom import constant
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
        self.end_date = datetime(2018, 7, 6, 16, 0, 0)

        # core function
        # self.real_condi_search_result()
        self.stock_info = self.kw.get_stock_basic_info()
        self.kospi = dict([(code, info) for code, info in self.stock_info.items() if info["market"] == "kospi"])
        # for code in code_list:
        #     info = self.stock_info[code]
        #     if not any(map(lambda x: x in info["stock_name"], constant.FILTER_KEYWORD)):
        #         del self.stock_info[code]

        # "단기_10min3p_급등주002" : 1
        # "단기_10min3p_급등주001" : 5
        # "단기_10min3p_스켈핑" : 4
        self.analysis("단기_10min3p_급등주002")
        self.analysis("단기_10min3p_급등주001")
        self.analysis("단기_10min3p_스켈핑")

    def analysis(self, condi_name):
        print("condi_name: %s" % condi_name)

        cur = self.db.real_condi_search.find({'market': 'kospi', 'condi_name': condi_name, 'event_type': 'I'})
        code_list = list(set([data['code'] for data in cur]))

        for code in [c for c in code_list if c in self.kospi]:
            fig = plt.figure(figsize=(20, 10))
            # plt.style.use('seaborn-whitegrid')

            stock_name = self.kospi[code]["stock_name"]
            cur = self.db.real_condi_search.find({'market': 'kospi',
                                                  'condi_name': condi_name,
                                                  'event_type': 'I',
                                                  'code': code})
            all_stocks = list(set([datetime(2018, 7, 25, data['date'].hour, data['date'].minute) for data in cur]))

            cur = self.db.time_series_min1.find({'code': code,
                                                 'date': {'$gte': datetime(2018, 7, 25, 8, 0, 0)}})\
                .sort('date', pymongo.ASCENDING)

            time_series = [(data['date'], data['시가']) for data in cur]
            x1 = [d[0] for d in time_series]
            y1 = [d[1] for d in time_series]
            ord_dict = OrderedDict(time_series)
            plt.plot(x1, y1)

            x2 = all_stocks
            y2 = [ord_dict.get(d) for d in all_stocks]
            plt.plot(x2, y2, 'v', color='red')

            plt.ylabel('Condi: {}, Stock: {}'.format(condi_name, stock_name))
            plt.grid()
            # plt.show()
            fig.savefig("{}_{}.png".format(condi_name.replace("/", "-"), stock_name))
            plt.close(fig)

        print('{} - Analysis End'.format(condi_name))


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
