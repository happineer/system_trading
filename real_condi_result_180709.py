

# built-in module
import sys
import pdb
import os
import re
import datetime as datetime_m
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
from collections import OrderedDict

from kiwoom.constant import KiwoomServerCheckTimeError
import multiprocessing

from matplotlib import pyplot as plt
from matplotlib import font_manager, rc

# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        # self.setupUi(self)  # load app screen
        self.logger = TTlog(logger_name="TTRealCondi")
        self.mongo = MongoClient()
        self.tt_db = self.mongo.TopTrader
        self.slack = Slacker(config_manager.get_slack_token())
        self.end_date = datetime(2018, 7, 6, 16, 0, 0)
        self.kw = Kiwoom()
        self.login()
        self.get_screen_no = {
            "min1": "3000",
            "min3": "3001",
            "min5": "3002",
            "min10": "3003",
            "min60": "3004",
            "day": "3005",
            "week": "3006",
            "month": "3007",
            "year": "3008"
        }

        # core function
        # self.real_condi_search_result()
        self.kospi, self.kosdaq = [dict(stock_info) for stock_info in self.get_stock_list()]
        font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/NanumGothic.ttf").get_name()
        rc('font', family=font_name)

        self.analysis('추천조건식02')
        self.analysis('급등/상승 추세조건')
        self.analysis('추천조건식01')
        self.analysis('Envelop횡단')
        self.analysis('스켈핑')

    def analysis(self, condi_name):
        print("condi_name: %s" % condi_name)

        cur = self.tt_db.real_condi_search.find({'market': 'kospi',
                                                 'condi_name': condi_name,
                                                 'event': 'I'})
        code_list = list(set([data['code'] for data in cur]))

        for code in code_list:
            fig = plt.figure()
            plt.style.use('seaborn-whitegrid')

            stock_name = self.kospi[code]
            cur = self.tt_db.real_condi_search.find({'market': 'kospi',
                                                     'condi_name': condi_name,
                                                     'event': 'I',
                                                     'code': code})
            all_stocks = list(set([datetime(2018, 7, 10, data['date'].hour, data['date'].minute) for data in cur]))

            cur = self.tt_db.time_series_min1.find({'code': code,
                                                    'date': {'$gt': datetime(2018, 7, 9, 16, 0, 0)}})\
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
        print('{} - Analysis End'.format(condi_name))

    def real_condi_search_result(self):
        kospi, kosdaq = [dict(stock_info) for stock_info in self.get_stock_list()]
        patt_code = re.compile("\[(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).*\] \* code: (\d{6})")
        patt_event_type = re.compile("\[(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).*\] \* event_type: ([A-Z])")
        patt_condi_index = re.compile("\[(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).*\] \* condi_index: (\d)")

        dict_condi = {
            0: '추천조건식02',
            1: '급등/상승 추세조건',
            2: '추천조건식01',
            3: 'Envelp횡단',
            4: '스켈핑'
        }
        lines = open("result.txt").read().strip().split("\n")
        result = []
        for i in range(len(lines))[::3]:
            try:
                yyyy, mm, dd, h, m, s, code = re.search(patt_code, lines[i]).groups()
                yyyy, mm, dd, h, m, s, event_type = re.search(patt_event_type, lines[i + 1]).groups()
                yyyy, mm, dd, h, m, s, condi_index = re.search(patt_condi_index, lines[i + 2]).groups()
                yyyy, mm, dd, h, m, s = [int(n) for n in (yyyy, mm, dd, h, m, s)]
                condi_name = dict_condi[int(condi_index)]
                date = datetime(yyyy, mm, dd, h, m, s)
                if code in kospi:
                    stock_name, market = kospi[code], "kospi"
                elif code in kosdaq:
                    stock_name, market = kosdaq[code], "kosdaq"

                result.append({
                    'date': date,
                    'code': code,
                    'stock_name': stock_name,
                    'market': market,
                    'event': event_type,
                    'condi_name': condi_name
                })

            except Exception as e:
                pdb.set_trace()
                print("[Error] parsing error")
        self.tt_db.real_condi_search.insert(result)
        print("Complete to store all stock data..")

    def login(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            exit(-1)
        self.logger.info("Login success")

    def get_stock_list(self):
        kospi_code_list = self.kw.get_code_list_by_market(0)
        kospi_stock_list = [[c, self.kw.get_master_stock_name(c)] for c in kospi_code_list]
        kospi_stock_list = [(c, name) for c, name in kospi_stock_list if not any(map(lambda x: x in name, constant.FILTER_KEYWORD))]
        kospi_stock_list.sort()

        kosdaq_code_list = self.kw.get_code_list_by_market(10)
        kosdaq_stock_list = [[c, self.kw.get_master_stock_name(c)] for c in kosdaq_code_list]
        kosdaq_stock_list = [(c, name) for c, name in kosdaq_stock_list if not any(map(lambda x: x in name, constant.FILTER_KEYWORD))]
        kosdaq_stock_list.sort()

        return kospi_stock_list, kosdaq_stock_list


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
