

# built-in module
import sys
import pdb
import os
from datetime import datetime

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
from util.slack import Slack

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
        self.slack = Slack(config_manager.get_slack_token())
        self.kw = Kiwoom()
        self.login()

        # ready to search condi
        self.load_stock_info()
        t = datetime.today()
        self.s_time = datetime(t.year, t.month, t.day, 9, 0, 0)  # 장 시작시간, 오전9시

        # fake trading
        self.timer = None
        self.start_timer()

        # core function
        # self.screen_no = 4000
        # self.N1, self.N2 = 0, 10

        self.screen_no = 4001
        self.N1, self.N2 = 10, 20

        self.real_condi_search()

    def load_stock_info(self):
        self.stock_dict = {}
        doc = self.tt_db.stock_information.find({})
        for d in doc:
            code = d["code"]
            self.stock_dict[code] = d
        self.logger.info("loading stock_information completed.")

    def start_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
        self.timer = QTimer()
        self.timer.timeout.connect(self.fake_check_to_sell)
        # self.timer.setSingleShot(True)
        self.timer.start(1000) # 1 sec interval

    def fake_check_to_sell(self):
        """

        :return:
        """

    def search_result(self, event_data):
        """

        :param event_data:
        :return:
        """
        curr_time = datetime.today()

        if curr_time < self.s_time:
            self.logger.info("=" * 100)
            self.logger.info("장 Open 전 입니다. 오전 9:00 이후에 검색 시작합니다.")
            self.logger.info("=" * 100)
            return

        # 실시간 조건검색 이력정보
        self.tt_db.real_condi_search.insert({
            'date': curr_time,
            'code': event_data["code"],
            'stock_name': self.stock_dict[event_data["code"]]["stock_name"],
            'market': self.stock_dict[event_data["code"]]["market"],
            'event': event_data["event_type"],
            'condi_name': event_data["condi_name"]
        })

    def real_condi_search(self):
        # callback fn 등록
        self.kw.reg_callback("OnReceiveRealCondition", "", self.search_result)
        # self.kw.notify_callback["OnReceiveRealCondition"] = self.search_condi

        condi_info = self.kw.get_condition_load()
        self.logger.info("실시간 조건 검색 시작합니다.")
        for condi_name, condi_id in list(condi_info.items())[self.N1:self.N2]:
            # 화면번호, 조건식이름, 조건식ID, 실시간조건검색(1)
            self.logger.info("화면번호: {}, 조건식명: {}, 조건식ID: {}".format(
                self.screen_no, condi_name, condi_id
            ))
            self.kw.send_condition(str(self.screen_no), condi_name, int(condi_id), 1)
            time.sleep(0.5)

    def login(self):
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            exit(-1)
        self.logger.info("Login success")


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
