# built-in module
import pdb
import sys
from datetime import datetime
from datetime import timedelta

# Visualization
import matplotlib as mpl
from PyQt5 import uic
# UI(PyQt5) module
from PyQt5.QtWidgets import *
from matplotlib import font_manager as fm
from matplotlib import pyplot as plt
# Database
from pymongo import MongoClient

# My modules
from config import config_manager as cfg_mgr
from database.db_manager import DBM
# Kiwoom module
from kiwoom.kw import Kiwoom
from trading.condi import ConditionalSearch
from trading.strategy import Strategy
from util.slack import Slack
from util.tt_logger import TTlog

# Data analysis


# load main UI object
ui = uic.loadUiType(cfg_mgr.MAIN_UI_PATH)[0]


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
        self.dbm = DBM('TopTrader')

        # Slack
        self.slack = Slack(cfg_mgr.get_slack_token())

        # Kiwoom
        self.kw = Kiwoom()
        self.login()
        cfg_mgr.STOCK_INFO = self.kw.get_stock_basic_info()

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
        try:
            path = 'c:/Windows/Fonts/D2Coding-Ver1.3-20171129.ttc'
            font_name = fm.FontProperties(fname=path).get_name()
            plt.rcParams["font.family"] = font_name
        except FileNotFoundError as e:
            path = 'c:/Windows/Fonts/D2Coding-Ver1.3.2-20180524.ttf'
            font_name = fm.FontProperties(fname=path).get_name()
            plt.rcParams["font.family"] = font_name

    def collect_1tick_data(self, code, stock_name, date):
        col_tick1 = self.db.time_series_tick1
        cur = col_tick1.find({'code': code, 'date': date})
        if cur.count() != 0:
            print("{}:{} Already save data. so Skip to save data !".format(code, stock_name))
            return

        s_date = date
        e_date = date + timedelta(days=1)
        raw_data = self.kw.stock_price_by_tick(code, tick="1", screen_no="1234",
                                               start_date=s_date, end_date=e_date)
        data = {
            'code': code,
            'stock_name': stock_name,
            'date': date,
            'time_series_1tick': [{'timestamp': _d['date'], '현재가': _d['현재가'], '거래량': _d['거래량']} for _d in raw_data]
        }
        # col_tick1.insert(data)
        return data

    def check_cache_tick1(self, code, s_date, e_date):
        col_tick1 = self.db.time_series_tick1
        s_base_date = datetime(s_date.year, s_date.month, s_date.day, 0, 0, 0)
        cur = col_tick1.find({'code': code, 'date': {'$gte': s_base_date, '$lte': e_date}})
        if cur.count() != 0:
            return True, cur
        return False, None

    def main(self):
        # 목표 !!!
        # 하루 단위의 조건검색 결과를 분석한다.

        # 사용자 지정 변수__S
        self.target_date = datetime.today()
        self.target_date = datetime(2018, 8, 2)  # temp code
        # 사용자 지정 변수__E

        # 조건검색식 load
        condi_info = self.kw.get_condition_load()
        strg_list = []
        cnt = 0
        condi_selector = 3
        # loop를 돌면서 각각의 조건검색식에 대해 결과 분석
        for condi_name, condi_index in condi_info.items():
            cnt += 1
            if condi_selector != cnt:
                continue
            # 특정일의 특정조건검색식을 특정전략으로 검증
            condi = ConditionalSearch.get_instance(condi_index, condi_name)

            self.logger.info("=======[ Smulation(%s) Start! ]=======" % condi.condi_name)
            strg = Strategy("short_trading.strategy", condi)
            strg.simulate(self.target_date)
            strg_list.append(strg)
            self.logger.info("=======[ Smulation(%s) End! ]=======" % condi.condi_name)
            self.logger.info("\n\n\n")

            if condi_selector == cnt:
                exit(0)

        self.logger.info("end")
        exit(0)


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
