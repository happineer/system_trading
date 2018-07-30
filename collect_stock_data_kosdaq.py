
import os
import pdb
import sys
import time
from pymongo import MongoClient
from config import config_manager
import datetime as datetime_m
from datetime import datetime, timedelta
from util.slack import Slack


def delay_min(t):
    for curr_time in range(t)[::-1]:
        print("delay(min) -> %s / %s" % (curr_time, t))
        time.sleep(60)


def main(duration_list):
    mongo = MongoClient()
    db = mongo.TopTrader
    today = datetime.today()
    end_date = datetime(today.year, today.month, today.day, 16, 0, 0)
    slack = Slack(config_manager.get_slack_token())

    for duration in duration_list:
        slack.send_message("[Automation] Start to collect stock data -> {}".format(duration))

        while True:
            cmd = "python collect_stock_data_time_unit_kosdaq.py {}".format(duration)
            print(cmd)
            os.system(cmd)
            error_status = db.urgent2.find({'type': 'error'}).next()
            ret = error_status['error_code']
            print("ret_code:{} -> python collect_stock_data_time_unit_kosdaq.py {}".format(ret, duration))
            if ret == -100:  # kiwoom server check time (mon~sat)
                delay = 20
                print("Delay {} minutes due to Kiwoom server check time. Mon~Sat".format(delay))
                print("Until : {}".format(datetime.today() + timedelta(minutes=delay)))
                delay_min(delay)
            elif ret == -101:  # kiwoom server check time (mon~sat)
                delay = 45
                print("Delay {} minutes due to Kiwoom server check time. Sun".format(delay))
                print("Until : {}".format(datetime.today() + timedelta(minutes=delay)))
                delay_min(delay)

            cur = db.time_series_temp2.find({'type': duration})
            if cur.count() == 0:  # exception case.. retry
                continue

            status = cur.next()
            if status['last'] == (status['total']-1) and status['end_date'] == end_date:
                print("Collecting & Storing Stock {} Data is completed!".format(duration))
                break
        slack.send_message("[Automation] Complete to collect stock data -> {}".format(duration))


if __name__ == "__main__":
    main([
        "min1",
        # "min3",
        # "min5",
        # "min10",
        # "min60",
        # "day",
        # "week",
        # "month"
    ])
