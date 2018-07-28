# built-in module
import sys
import pdb
import os
import pandas as pd
import time
import re

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

from datetime import datetime

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
        self.tt_logger = TTlog()
        self.mongo = MongoClient()
        self.db = self.mongo.TopTrader
        self.kw = Kiwoom()
        self.test()

    def test(self):
        # Login
        err_code = self.kw.login()
        if err_code != 0:
            self.tt_logger.error("Login Fail")
            return
        self.tt_logger.info("Login success")

        # kospi_codes = self.kw.get_code_list_by_market(0)
        # kosdaq_codes = self.kw.get_code_list_by_market(10)
        # kospi = [(self.kw.get_master_stock_name(code), code) for code in kospi_codes]
        # kosdaq = [(self.kw.get_master_stock_name(code), code) for code in kosdaq_codes]
        # with open("stock_list.txt", "w", encoding="utf-8") as f:
        #     for sn, code in kospi:
        #         f.write("{}, {}\n".format(sn, code))
        #     for sn, code in kosdaq:
        #         f.write("{}, {}\n".format(sn, code))

        # with open("stock_list.txt", encoding="utf-8") as f:
        #     all_stocks = [data.split(", ") for data in f.read().strip().split("\n")]
        #     all_stocks = [(stock_name, code) for stock_name, code in all_stocks
        #                   if not (stock_name.endswith("우") or stock_name.endswith("우B"))]
        #
        # with open("stock_list_without_우선주.txt", "w", encoding="utf-8") as f:
        #     for sn, code in all_stocks:
        #         f.write("{}, {}\n".format(sn, code))

        # p1 = re.compile("[0-9]호스팩")
        # p2 = re.compile("[0-9]호")
        #
        # def is_derivatives(stock_name):
        #     ret1 = re.search(p1, stock_name)
        #     ret2 = re.search(p2, stock_name)
        #     kw_list = ["ETN", "ARIRANG", "KODEX", "KINDEX", "KBSTAR", "HANARO", "SMART", "TIGER", "KOSEF"]
        #     ret3 = any([kw in stock_name for kw in kw_list])
        #     return bool(ret1 or ret2 or ret3)
        #
        # with open("stock_list_without_우선주.txt", encoding="utf-8") as f:
        #     all_stocks = [data.split(", ") for data in f.read().strip().split("\n")]
        #     all_stocks = [(stock_name, code) for stock_name, code in all_stocks
        #                   if not is_derivatives(stock_name)]
        #
        #     with open("stock_list_without_우선주_파생상품.txt", "w", encoding="utf-8") as f:
        #         for sn, code in all_stocks:
        #             f.write("{}, {}\n".format(sn, code))

        # def is_high_risk(stock_name):
        #     high_risk_stock_list = [
        #         "알보젠코리아", "삼광글라스", "한국특수형강",  # 관리종목(코스피)
        #         "한솔PNS", "STX중공업", "TIGER은행", "에이리츠",
        #         "차이나하오란", "에이스침대", "행남사", "쌍용정보통신", "엠벤처투자",  # 관리종목(코스닥)
        #         "위너지스", "에스마크", "C&S자산관리", "이디", "UCI", "에임하이",
        #         "바이오제네틱", "레이젠", "에이앤티앤", "이에스에이", "트레이스",
        #         "와이디온라인", "현진소재", "에프티이앤이", "한솔인티큐브",
        #         "동원", "삼화전기", "제일제강", "와이오엠", "삼원테크",  # 투자주의/경고/위험
        #         "엠벤처투자", "위너지스", "에스마크", "C&S자산관리", "이디",  # 투자주의환기
        #         "더블유에프엠", "마제스타", "UCI", "에임하이", "KD건설", "레이젠",
        #         "재영솔루텍", "이에스에이", "트레이스", "와이디온라인", "현진소재",
        #         "에프티이앤이", "씨씨에스", "한솔인티큐브", "케이디 네이쳐", "일경산업개발",
        #         "에스제이케이", "코디", "넥스지", "수성",
        #         "하이트진로홀", "유유제약2우B", "노루홀딩스우", "부국증권우",  # 초저유동성종목
        #         "BYC", "동양우", "동양2우B", "한양증권우", "한국유리우", "코오롱우",
        #         "텍센타이어1우", "미원상사", "유화증권", "유화증권우", "대뎍GDS우",
        #         "NPC우", "세방우", "성신양회3우B", "녹십자홀딩스2", "넥센우"
        #     ]
        #     high_risk_stock_list = list(set(high_risk_stock_list))
        #     return stock_name in high_risk_stock_list
        #
        # with open("stock_list_without_우선주_파생상품.txt", encoding="utf-8") as f:
        #     all_stocks = [data.split(", ") for data in f.read().strip().split("\n")]
        #     all_stocks = [(stock_name, code) for stock_name, code in all_stocks
        #                   if not is_high_risk(stock_name)]
        #
        # with open("stock_list_without_우선주_파생상품_위험상품.txt", "w", encoding="utf-8") as f:
        #     for sn, code in all_stocks:
        #         f.write("{}, {}\n".format(sn, code))

        # with open("stock_list_without_우선주_파생상품_위험상품.txt", encoding="utf-8") as f:
        #     all_stocks = [data.split(", ") for data in f.read().strip().split("\n")]
        #
        # stock_state = []
        # for i, stock in enumerate(all_stocks):
        #     stock_name, code = stock
        #     is_gwansim = self.kw.dynamicCall("GetMasterStockState(QString)", code)
        #     print("stock: {}, result: {}".format(stock_name, is_gwansim))
        #     stock_state += is_gwansim.split("|")
        #
        # pdb.set_trace()
        # stock_state = list(set(stock_state))

        with open("stock_list_without_우선주_파생상품_위험상품.txt", encoding="utf-8") as f:
            all_stocks = [data.split(", ") for data in f.read().strip().split("\n")]

        total = len(all_stocks) - 1589
        for i, stock in enumerate(all_stocks[1589:]):
            print("{}/{}".format(i+1, total))
            try:
                stock_name, code = stock
                print("stock_name: {}".format(stock_name))
                s_date, e_date = datetime(2018, 7, 15, 0, 0, 0), datetime(2018, 7, 16, 16, 0, 0)
                doc = self.kw.stock_price_by_day(code, screen_no="2000", start_date=s_date, end_date=e_date)
                price, volumn = doc[0]['시가'], doc[0]['거래량']
                self.db.day_stat.insert({'code': code, 'stock': stock_name,
                                         'price': price, 'volumn': volumn})
            except Exception as e:
                print("Exception happen")
        pdb.set_trace()

        # cur = self.db.day_stat.find({"price": {"$gt": 1000, "$lt": 100000}, "volumn": {"$gt": 100000}})
        # cnt = cur.count()
        # print("Count: {}".format(cnt))
        # for data in cur:
        #     code, stock = data["code"], data["stock"]
        #     print("stock: {}".format(stock))


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
