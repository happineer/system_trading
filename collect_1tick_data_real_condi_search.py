# built-in module
import sys
import pdb
import os
from datetime import datetime
from datetime import timedelta

import pandas as pd
import time


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
        # self.setupUi(self)  # load app screen
        self.logger = TTlog().logger
        self.dbm = DBM('TopTrader')
        self.mongo = MongoClient()
        self.db = self.mongo.TopTrader
        self.slack = Slack(config_manager.get_slack_token())
        self.kw = Kiwoom()
        self.login()
        self.main()

    def load_tick_data(self, code, stock_name, date, tick="1", screen_no="1234"):
        """특정 종목의 하루단위 tick data를 가져오는 함수
        tick_data가 DB에 있으면 DB에서 가져오고, 없으면 kw module로부터 가져온다.

        :param code:
        :param stock_name:
        :param date:
        :param tick:
        :param screen_no:
        :return:
        """
        ret, cur = self.dbm.check_tick_cache(code, date, tick="1")

        if ret:
            tick_data = cur.next()
        else:
            base_date = datetime(date.year, date.month, date.day, 0, 0, 0)
            raw_data = self.kw.stock_price_by_tick(code, tick=tick, screen_no=screen_no, date=base_date)
            tick_data = {
                'code': code,
                'stock_name': stock_name,
                'date': base_date,
                'time_series_1tick': [{'timestamp': _d['date'], '현재가': _d['현재가'], '거래량': _d['거래량']} for _d in raw_data]
            }
        return tick_data

    def collect_tick_data(self, code, stock_name, s_date, e_date, tick="1", screen_no="1234"):
        """특정 종목의 일정 기간의 tick data를 DB에 저장하는 함수
        DB에 이미 값이 저장되어 있으면 저장하지 않고 skip 한다.
        s_date, e_date는 초단위까지 지정이 가능하지만, 저장은 일단위로 저장한다.
        tick은 1, 3, 5, 10, 30 선택 가능하다.

        :param code:
        :param stock_name:
        :param tick:
        :param s_date:
        :param e_date:
        :return:
        """
        s_base_date = datetime(s_date.year, s_date.month, s_date.day, 0, 0, 0)
        e_base_date = datetime(e_date.year, e_date.month, e_date.day, 0, 0, 0)
        days = (e_base_date - s_base_date).days + 1
        date_list = [s_base_date + timedelta(days=x) for x in range(0, days)]
        for base_date in date_list:
            ret, cur = self.dbm.check_tick_cache(code, base_date, tick="1")
            if ret:
                self.logger.debug("No need to save data. already has data in DB")
                continue

            raw_data = self.kw.stock_price_by_tick(code, tick=tick, screen_no=screen_no, date=base_date)
            tick_data = {
                'code': code,
                'stock_name': stock_name,
                'date': base_date,
                'time_series_1tick': [{'timestamp': _d['date'], '현재가': _d['현재가'], '거래량': _d['거래량']} for _d in raw_data]
                # 'time_series': [{'timestamp': _d['date'], '현재가': _d['현재가'], '거래량': _d['거래량']} for _d in raw_data]
            }
            # DB에 없으면 수행되는 부분이라서 insert 함수를 사용.
            self.dbm.save_tick_data(tick_data, tick="1")

    def main(self):
        # 사용자 정의 부분_S
        # 8/2일자 조건검색식으로 검출된 모든 종목의 1tick data를 수집한다.
        with open("base_date_when_collect_tick_data.txt") as f:
            year, month, day = [int(i) for i in f.read().strip().split(" ")]
        self.base_date = datetime(year, month, day)
        # 사용자 정의 부분_E

        # kospi, kosdaq 모든 종목의 코드와 종목명 정보를 불러온다.
        self.stock_info = self.kw.get_stock_basic_info()

        code_list = self.dbm.get_code_list_condi_search_result(self.base_date)
        code_list.sort()
        self.dbm.record_collect_tick_data_status("START", self.base_date, tick="1")
        for num, code in enumerate(code_list, 1):
            stock_name = self.stock_info[code]["stock_name"]
            if self.dbm.already_collect_tick_data(code, self.base_date, tick="1"):
                self.logger.debug("{}/{} - {}:{} Skip. Already saved data!".format(num, len(code_list), code, stock_name))
                continue

            self.logger.debug("{}/{} - {}:{} Start !".format(num, len(code_list), code, stock_name))
            self.collect_tick_data(code, stock_name, self.base_date, self.base_date, tick="1", screen_no="1234")
            self.logger.debug("{}/{} - {}:{} Completed !".format(num, len(code_list), code, stock_name))

            self.dbm.save_collect_tick_data_history(code, self.base_date, tick="1")
            self.dbm.record_collect_tick_data_status("WORKING", self.base_date, tick="1")

        self.dbm.record_collect_tick_data_status("END", self.base_date, tick="1")
        self.logger.debug("save all 1tick information..")
        exit(0)  # program exit

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
