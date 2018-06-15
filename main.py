
# built-in module
import sys
import pdb
import os
import pandas as pd
import time
import logging
import logging.handlers

# UI(PyQt5) module
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

from slacker import Slacker

from kiwoom.kw import Kiwoom
from config import config_manager

# load main UI object
ui = uic.loadUiType(config_manager.MAIN_UI_PATH)[0]

logger = logging.getLogger("TopTrader")
formatter = logging.Formatter('[%(asctime)s|%(levelname)s|%(funcName)s:%(lineno)s]%(message)s')
fileMaxByte = 1024 * 1024 * 10 # 10MB
log_path = "D:/work/TopTrader_log/TopTrader.log"
file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=fileMaxByte, backupCount=1000)
stream_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


# main class
class TopTrader(QMainWindow, ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # load app screen
        self.boot_system()

    def boot_system(self):
        self.kw = Kiwoom()
        self.test()
        self.slack = Slacker(config_manager.SLACK_TOKEN)

    def test(self):
        self.test_login()
        """
        server = self.kw.get_connect_state()
        self.kw.get_server_gubun()
        code_name = self.kw.get_master_stock_name('207940')  # 삼바
        THEME_ORDER = 1
        theme_list = self.kw.get_theme_group_list(THEME_ORDER)
        code_list = self.kw.get_code_list_by_market(0)
        search_method = self.kw.get_condition_load()
        """
        # data = self.kw.stock_min_data('207940', tick='1')  # 삼바
        # pdb.set_trace()
        data = self.kw.stock_day_data('207940', date='20180615')  # 삼바
        pdb.set_trace()
        data = self.kw.stock_week_data('207940', s_date='20180611', e_date='20180615')  # 삼바
        pdb.set_trace()
        data = self.kw.stock_month_data('207940', s_date='20180611', e_date='20180615')  # 삼바
        pdb.set_trace()

    def test_login(self):
        logger.info("Try Login")
        err_code = self.kw.login()
        if err_code != 0:
            logger.error("Login Fail")
            return
        logger.info("Login success")


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
