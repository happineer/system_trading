
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
        duration = sys.argv[1]
        self.logger = TTlog(logger_name="TT"+duration)
        self.mongo = MongoClient()
        self.tt_db = self.mongo.TopTrader
        self.slack = Slacker(config_manager.get_slack_token())
        with open("collect_stock_data_last_date.txt") as f:
            date_str = f.read().strip().split(" ")

        self.end_date = datetime(*date_str)
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
        if duration.startswith("min"):
            self.collect_n_save_data_min(duration)
        else:
            self.collect_n_save_data(duration)

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

    def get_last_data(self, cur, duration):
        current_flag = True
        if duration.startswith("min"):
            first_date = datetime(2018, 7, 1, 0, 0, 0)
        else:
            first_date = datetime(2018, 6, 1, 0, 0, 0)

        # 최초 저장하는 경우
        if cur.count() == 0:
            s_date, e_date, s_index = first_date, self.end_date, 0
        else:
            data = cur.next()
            if (data['last'] + 1) != data['total']:
                # 지난번에 저장하다가 중간에 멈춘 경우
                if data['end_date'] != self.end_date:
                    s_date, e_date, s_index = data['start_date'], data['end_date'], data['last'] + 1
                    current_flag = False
                # 이번에 저장하다가 중간에 멈춘 경우
                else:
                    s_date, e_date, s_index = data['start_date'], self.end_date, data['last'] + 1
            else:
                # 지난번에 저장을 완료, 이번에 저장해야 하는 경우
                if data['end_date'] != self.end_date:
                    s_date, e_date, s_index = data['end_date'], self.end_date, 0
                # 이번에 저장을 완료
                else:
                    s_date, e_date, s_index = data['end_date'], self.end_date, data['last'] + 1
        return s_date, e_date, s_index, current_flag

    def collect_n_save_data_min(self, duration):
        """
        코스피 종목의 분단위 데이터를 수집한다.

        1. 한번도 db에 저장한적이 없다면 6/1일부터 오늘까지의 데이터를 저장한다.
        2. 지난번에 저장하다가 중간에 멈췄다면, 나머지 작업을 모두 완료 후, 해당시점의 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.
        3.   이번에 저장하다가 중간에 멈췄다면, 이전 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.
        4. 지난번에 저장을 완료했다면, 해당시점의 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.

        :param duration: min1, min3, min5, min10, min60 중 하나의 값
        :return:
        """
        stock_list = self.get_stock_list()
        cur = self.tt_db.time_series_temp.find({'type': duration})
        s_date, e_date, s_index, current_flag = self.get_last_data(cur, duration)

        if not current_flag:
            msg = "[{}] {} ~ {}. start to collect stock data. this is previous process.".format(
                duration, s_date, e_date, e_date, self.end_date
            )
        else:
            msg = "[{}] {} ~ {}. start to collect stock data. this is current process.".format(
                duration, s_date, e_date
            )
        self.slack.chat.post_message('#general', msg)

        col = {
            "min1": self.tt_db.time_series_min1,
            "min3": self.tt_db.time_series_min3,
            "min5": self.tt_db.time_series_min5,
            "min10": self.tt_db.time_series_min10,
            "min60": self.tt_db.time_series_min60
        }[duration]
        fn = self.kw.stock_price_by_min

        total = len(stock_list)
        msg = "[{}] {} / {} -> start to collect stock data".format(duration, s_index, total)
        self.slack.chat.post_message('#general', msg)

        for i, stock in enumerate(stock_list[s_index:], s_index):
            code, stock_name = stock
            self.logger.info("%s/%s - %s/%s" % (i, total, code, stock_name))
            self.logger.info("time_series_{}".format(duration))

            try:
                doc = fn(code, tick=duration.strip("min"), screen_no=self.get_screen_no[duration],
                         start_date=s_date, end_date=e_date)
            except KiwoomServerCheckTimeError as e:
                self.logger.error("[KiwoomServerCheckTimeError] {}".format(duration))
                self.tt_db.urgent.update({'type': 'error'},
                                         {'type': 'error', 'error_code': e.error_code},
                                         upsert=True)
                exit(0)

            self.upsert_db(col, doc)
            self.tt_db.time_series_temp.update({'type': duration},
                                               {'type': duration,
                                                'code': code,
                                                'stock_name': stock_name,
                                                'last': i,
                                                'start_date': s_date,
                                                'end_date': e_date,
                                                'total': total},
                                               upsert=True)
            self.tt_db.urgent.update({'type': 'error'},
                                     {'type': 'error', 'error_code': 0},
                                     upsert=True)
        exit(0)  # Program exit

    def collect_n_save_data(self, duration):
        """
        코스피 종목의 분단위 데이터를 제외한 나머지 데이터를 수집한다.

        1. 한번도 db에 저장한적이 없다면 6/1일부터 오늘까지의 데이터를 저장한다.
        2. 지난번에 저장하다가 중간에 멈췄다면, 나머지 작업을 모두 완료 후, 해당시점의 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.
        3.   이번에 저장하다가 중간에 멈췄다면, 이전 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.
        4. 지난번에 저장을 완료했다면, 해당시점의 e_date 부터 오늘까지의 데이터를 전 종목에 대해 저장한다.

        :param duration: str - day, week, month, year 중 하나의 값
        :return:
        """
        stock_list = self.get_stock_list()
        cur = self.tt_db.time_series_temp.find({'type': duration})
        s_date, e_date, s_index, current_flag = self.get_last_data(cur, duration)

        if not current_flag:
            msg = "[{}] {} ~ {}. start to collect stock data. this is previous process.".format(
                duration, s_date, e_date, e_date, self.end_date
            )
        else:
            msg = "[{}] {} ~ {}. start to collect stock data. this is current process.".format(
                duration, s_date, e_date
            )
        self.slack.chat.post_message('#general', msg)

        col = {
            "day": self.tt_db.time_series_day,
            "week": self.tt_db.time_series_week,
            "month": self.tt_db.time_series_month,
            "year": self.tt_db.time_series_year
        }[duration]

        fn = {
            "day": self.kw.stock_price_by_day,
            "week": self.kw.stock_price_by_week,
            "month": self.kw.stock_price_by_month
            # "year": self.kw.stock_price_by_year
        }[duration]

        total = len(stock_list)
        msg = "[{}] {} / {} -> start to collect stock data".format(duration, s_index, total)
        self.slack.chat.post_message('#general', msg)

        for i, stock in enumerate(stock_list[s_index:], s_index):
            code, stock_name = stock
            self.logger.info("%s/%s - %s/%s" % (i, total, code, stock_name))
            self.logger.info("time_series_{}".format(duration))
            try:
                doc = fn(code, screen_no=self.get_screen_no[duration], start_date=s_date, end_date=e_date)
            except KiwoomServerCheckTimeError as e:
                self.logger.error("[KiwoomServerCheckTimeError] {}".format(duration))
                self.tt_db.urgent.update({'type': 'error'},
                                         {'type': 'error', 'error_code': e.error_code},
                                         upsert=True)
                exit(0)
            self.upsert_db(col, doc)
            self.tt_db.time_series_temp.update({'type': duration},
                                               {'type': duration,
                                                'code': code,
                                                'stock_name': stock_name,
                                                'last': i,
                                                'start_date': s_date,
                                                'end_date': e_date,
                                                'total': total},
                                               upsert=True)

            self.tt_db.urgent.update({'type': 'error'},
                                     {'type': 'error', 'error_code': 0},
                                     upsert=True)
        exit(0)  # Program exit


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
