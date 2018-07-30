

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
from kiwoom.constant import KiwoomServerCheckTimeError
import multiprocessing

# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        # self.setupUi(self)  # load app screen
        self.logger = TTlog(logger_name="RealCondi").logger
        self.mongo = MongoClient()
        self.tt_db = self.mongo.TopTrader
        self.slack = Slacker(config_manager.get_slack_token())
        self.kw = Kiwoom()
        self.login()

        # core function
        self.real_condi_search()

    def result_real_condi_search(self, data):
        self.logger.info("---- [TopTrader] result_real_condi_search ----")
        data['date'] = datetime.now()
        del data["kw_event"]
        self.tt_db.real_condi_search.insert(data)
        print("실시간 조건 검색 저장 완료!")

    def real_condi_4000(self, data):
        data['date'] = datetime.now()
        data['code_list'] = data['code_list'].strip(";").split(";")
        del data['next']
        self.tt_db.real_condi_4000.insert(data)
        print("실시간 조건 검색 - 추천조건식02 저장 완료")

    def real_condi_4001(self, data):
        data['date'] = datetime.now()
        data['code_list'] = data['code_list'].strip(";").split(";")
        del data['next']
        self.tt_db.real_condi_4001.insert(data)
        print("실시간 조건 검색 - 급등/상승_추세조건 저장 완료")

    def real_condi_4002(self, data):
        data['date'] = datetime.now()
        data['code_list'] = data['code_list'].strip(";").split(";")
        del data['next']
        self.tt_db.real_condi_4002.insert(data)
        print("실시간 조건 검색 - 추천조건식01 저장 완료")

    def real_condi_4003(self, data):
        data['date'] = datetime.now()
        data['code_list'] = data['code_list'].strip(";").split(";")
        del data['next']
        self.tt_db.real_condi_4003.insert(data)
        print("실시간 조건 검색 - Envelop횡단 저장 완료")

    def real_condi_4004(self, data):
        data['date'] = datetime.now()
        data['code_list'] = data['code_list'].strip(";").split(";")
        del data['next']
        self.tt_db.real_condi_4004.insert(data)
        print("실시간 조건 검색 - 스켈핑 저장 완료")

    def real_condi_search(self):
        self.kw.get_condition_load()
        # self.kw.notify_fn['4000'] = self.real_condi_4000
        # self.kw.notify_fn['4001'] = self.real_condi_4001
        # self.kw.notify_fn['4002'] = self.real_condi_4002
        # self.kw.notify_fn['4003'] = self.real_condi_4003
        # self.kw.notify_fn['4004'] = self.real_condi_4004
        self.kw.notify_fn['_on_receive_real_condition'] = self.result_real_condi_search

        ret = self.kw.send_condition('4000', '단기_10min3p_급등주002', 5, 1)
        ret = self.kw.send_condition('4001', '단기_10min3p_급등주001', 1, 1)
        ret = self.kw.send_condition('4002', '단기_10min3p_스켈핑', 4, 1)
        print("real_condi_search end")

    def login(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            exit(-1)
        self.logger.info("Login success")

    def upsert_db(self, col, datas):
        self.logger.info("Upsert Data to DB")
        s_time = time.time()
        for doc in datas:
            # col.update(condition, new_data, upsert=True)
            col.update({'date': doc['date'], 'code': doc['code']}, doc, upsert=True)
        e_time = time.time()
        print("Time: ", int(e_time-s_time))

    def get_stock_list(self):
        kospi_code_list = self.kw.get_code_list_by_market(0)
        stock_list = [[c, self.kw.get_master_stock_name(c)] for c in kospi_code_list]
        stock_list = [(c, name) for c, name in stock_list if not any(map(lambda x: x in name, constant.FILTER_KEYWORD))]
        stock_list.sort()
        return stock_list


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
