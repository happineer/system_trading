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
        # self.setupUi(self)  # load app screen
        self.logger = TTlog().logger
        self.kw = Kiwoom()
        self.login()
        self.test()

    def login(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.logger.error("Login Fail")
            return
        self.logger.info("Login success")

    def test(self):
        acc_no = self.kw.get_login_info("ACCNO")
        acc_no = acc_no.strip(";")  # 계좌 1개를 가정함.
        self.kw.계좌평가잔고내역요청("계좌평가잔고내역요청", acc_no, "", "1", "3000")
        self.kw.set_account(acc_no)
        self.kw.시장가_신규매도('217620', 210)
        self.kw.당일실현손익상세요청("당일실현손익상세요청", acc_no, "", "217620", "3001")
        self.kw.계좌수익률요청("계좌수익률요청", acc_no, "3002")
        ret = self.kw.get_basic_info('066570', "1001")
        self.kw.get_chegyul_info('066570', '1003')
        ret = self.kw.get_hoga_info('066570', '1004')
        self.kw.job_categ_index('001', "4001")

        # market = [kospi, kosdaq]
        # code = 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ),
        #        201:KOSPI200, 302:KOSTAR, 701: KRX100 나머지 ※ 업종코드 참고
        self.kw.job_categ_price(market='kospi', code='002', screen_no="4001")
        ret = self.kw.rapidly_rising_vol_stock(
            "001",  # 시장구분
            "1",  # 정렬구분
            "1",  # 시간구분
            "10",  # 거래량구분
            "60",  # 시간
            "1",  # 종목조건
            "0",  # 가격구분
            "4002"  # 화면번호
        )  # 거래량급증요청 (opt10023)
        ret = self.kw.rapidly_swing_price_stock(
            "001",  # 시장구분
            "1",    # 등락구분(1:급등, 2:급락)
            "1",    # 시간구분(1:분전, 2:일전)
            "60",   # 시간
            "00010",# 거래량구분(00000:전체조회, 00010:만주이상, 00050:5만주이상, 00100:10만주이상, 00150:15만주이상, 00200:20만주이상, 00300:30만주이상, 00500:50만주이상, 01000:백만주이상)
            "1",    # 종목조건(0:전체조회,1:관리종목제외, 3:우선주제외, 5:증100제외, 6:증100만보기, 7:증40만보기, 8:증30만보기)
            "0",    # 신용조건(0:전체조회, 1:신용융자A군, 2:신용융자B군, 3:신용융자C군, 4:신용융자D군, 9:신용융자전체)
            "1019"  # 화면번호
        )  # 가격급등락요청 (opt10019)


        # 미구현 TR -------------------------------------------------------------
        # self.kw.job_categ_by_min()
        # self.kw.job_categ_by_day()
        # self.kw.job_categ_by_week()
        # self.kw.job_categ_by_month()
        # self.kw.job_categ_by_year()

        # self.kw.?()  # 전일대비등락률상위요청 (opt10027)
        # self.kw.  # 가격급등락요청 (opt10019)
        # 미구현 TR -------------------------------------------------------------
        print("end")


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

