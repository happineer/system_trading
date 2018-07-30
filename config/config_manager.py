import pdb
import os.path
from pymongo import MongoClient

MAIN_UI_PATH = "./ui/main.ui"
KIWOOM_PROG_ID = "KHOPENAPI.KHOpenAPICtrl.1"
SLACK_TOKEN = ""

ROOT_PATH = os.path.dirname(os.path.abspath(__file__)).replace("config", "")
CFG_PATH = os.path.join(ROOT_PATH, "config")
STOCK_INFO = {}


def get_slack_token():
    global SLACK_TOKEN
    mongo = MongoClient()
    SLACK_TOKEN = mongo.TopTrader.config.find({}).next()["slack_token"]
    return SLACK_TOKEN
