
import os
import pdb
import sys
import time
from pymongo import MongoClient
from slacker import Slacker
from config import config_manager
import datetime


def print_n_noti_slack(slack, msg):
    print(msg)
    slack.chat.post_message('#general', msg)


def delay(t):
    for curr_time in range(t)[::-1]:
        print("delay(min) -> %s / %s" % (curr_time, t))
        time.sleep(60)


def main(duration_list):
    mongo = MongoClient()
    db = mongo.TopTrader
    end_date = datetime.datetime(2018, 7, 4, 16, 0, 0)
    slack = Slacker(config_manager.get_slack_token())

    for duration in duration_list:
        print_n_noti_slack(slack, "[Automation] Start to collect stock data -> {}".format(duration))

        while True:
            cmd = "python collect_stock_data_time_unit.py {}".format(duration)
            print(cmd)
            os.system(cmd)
            error_status = db.urgent.find({'type': 'error'}).next()
            ret = error_status['error_code']
            print("ret_code:{} -> python collect_stock_data_time_unit.py {}".format(ret, duration))
            if ret == -100:  # kiwoom server check time (mon~sat)
                print("Delay 15 minutes due to Kiwoom server check time. Mon~Sat")
                print("Until : {}".format(datetime.datetime.today() + datetime.timedelta(minutes=10)))
                delay(2)
            elif ret == -101:  # kiwoom server check time (mon~sat)
                print("Delay 40 minutes due to Kiwoom server check time. Sun")
                print("Until : {}".format(datetime.datetime.today() + datetime.timedelta(minutes=40)))
                delay(40)

            cur = db.time_series_temp.find({'type': duration})
            if cur.count() == 0:  # exception case.. retry
                continue

            status = cur.next()
            if status['last'] == (status['total']-1) and status['end_date'] == end_date:
                print("Collecting & Storing Stock {} Data is completed!".format(duration))
                break
        print_n_noti_slack(slack, "[Automation][{}] Complete to collect & save data...".format(duration))


if __name__ == "__main__":
    # main(sys.argv[1:])
    main(["min1",
          "min3",
          "min5",
          "min10",
          "min60",
          "day",
          "week",
          "month",
          "year",
          ])
