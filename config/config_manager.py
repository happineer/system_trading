import pdb
import os.path
from pymongo import MongoClient

from util import constant

MAIN_UI_PATH = "./ui/main.ui"
KIWOOM_PROG_ID = "KHOPENAPI.KHOpenAPICtrl.1"
SLACK_TOKEN = ""


STOCK_MONITOR = False
ACCOUNT_MONITOR = True

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).replace("config", "")
CFG_PATH = os.path.join(ROOT_PATH, "config")
STOCK_INFO = {}

# runtime mode
MODE = ""


def get_slack_token():
    global SLACK_TOKEN
    mongo = MongoClient()
    SLACK_TOKEN = mongo.TopTrader.config.find({}).next()["slack_token"]
    return SLACK_TOKEN


def set_mode(mode):
    global MODE
    if mode not in [constant.RELEASE, constant.DEBUG]:
        raise Exception('[config_manager] Runtime mode should be one of [constant.RELEASE, constant.DEBUG]')
    MODE = mode


def debug_mode():
    return MODE == constant.DEBUG
