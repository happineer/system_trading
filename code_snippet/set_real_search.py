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
        self.kw = Kiwoom()
        self.login()

        self.test()

    def login(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            return
        self.tt_logger.info("Login success")

        self.set_account()

    def set_account(self):
        print("request account number")
        ret = self.kw.get_login_info("ACCNO")
        self.account_no = ret.strip(";").split(";")[0]

    def test(self):
        print("send_order")
        self.kw.send_order('매수', '5000', self.account_no, '1', '066570', 1, 85000, '03', '')

    def realtime_search(self):
        lg_code = '066570'
        # 주식시세 -> 모든 데이터가 주식체결에 다 포함되어 있어서, 실제로 주식체결 데이터가 들어옴.
        # ret = self.kw.set_real_reg('4000', lg_code, '10;11;12;13;14;16;17;27;28;', '0')
        # time.sleep(0.5)

        # 주식체결
        # ret = self.kw.set_real_reg('4001', lg_code, '9001;10;13', '0')
        # time.sleep(0.5)

        # 주식우선호가
        # ret = self.kw.set_real_reg('4002', lg_code, '27;28;', '0')
        # time.sleep(0.5)

        # 주식호가잔량
        # ret = self.kw.set_real_reg('4003', lg_code, '41;51;61;71;', '1')
        # time.sleep(0.5)

        # 주식당일거래원
        # ret = self.kw.set_real_reg('4004', lg_code, '41;51;61;71;', '1')
        # time.sleep(0.5)

        # 주식예상체결 -> 주식체결이 될 가능성이...
        # ret = self.kw.set_real_reg('4005', lg_code, '20;10;11;12;15;13;25', '1')
        # time.sleep(0.5)
        #
        # # 주식종목정보
        # ret = self.kw.set_real_reg('4006', lg_code, '297;592;593;305;306;307;689;594;382;370;300', '1')
        # time.sleep(0.5)
        #
        # 업종지수
        # 업종코드 : 001:종합(kospi), 002:대형주, 003:중형주, 004:소형주, 101:종합(kosdaq), 201:kospi200, 302:kostar
        # ret = self.kw.set_real_reg('4007', '001', '20;10;11;12;15;13;14;16;17;18;25;26', '1')
        # time.sleep(0.5)
        #
        # # 업종등락
        # ret = self.kw.set_real_reg('4008', '001', '20;252;251;253;255;254;13;14;10;11;12;256;257;25', '1')
        # time.sleep(0.5)

        # 장시작시간
        # ret = self.kw.set_real_reg('4009', lg_code, '215;20;214', '1')
        # time.sleep(0.5)

        # 주문체결
        # ret = self.kw.set_real_reg('4010', lg_code, '9201;9203;9205;9001;912;913;302;900;901;902;903;904;905;906;907;908;909;910;911;10;27;28;914;915;938;939;919;920;921;922;923', '1')
        # time.sleep(0.5)
        #
        # # 잔고
        # ret = self.kw.set_real_reg('4011', lg_code, '9201;9001;917;916;302;10;930;931;932;933;945;946;950;951;27;28;307;8019;957;958;918;990;991;992;993;959;924', '1')
        # time.sleep(0.5)

        print("실시간 검색 요청!")


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
