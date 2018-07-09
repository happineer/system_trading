
import os
import pdb
import sys
import time
from pymongo import MongoClient
from config import config_manager
import datetime
from util.tt_slack import TTSlack


def delay_min(t):
    for curr_time in range(t)[::-1]:
        print("delay(min) -> %s / %s" % (curr_time, t))
        time.sleep(60)


def main(duration_list):
    mongo = MongoClient()
    db = mongo.TopTrader
    with open("collect_stock_data_last_date.txt") as f:
        date_str = f.read().strip().split(" ")
    end_date = datetime.datetime(*date_str)
    t_slack = TTSlack()

    for duration in duration_list:
        t_slack.notify("[Automation] Start to collect stock data -> {}".format(duration))

        while True:
            cmd = "python collect_stock_data_time_unit.py {}".format(duration)
            print(cmd)
            os.system(cmd)
            error_status = db.urgent.find({'type': 'error'}).next()
            ret = error_status['error_code']
            print("ret_code:{} -> python collect_stock_data_time_unit.py {}".format(ret, duration))
            if ret == -100:  # kiwoom server check time (mon~sat)
                delay = 20
                print("Delay {} minutes due to Kiwoom server check time. Mon~Sat".format(delay))
                print("Until : {}".format(datetime.datetime.today() + datetime.timedelta(minutes=delay)))
                delay_min(delay)
            elif ret == -101:  # kiwoom server check time (mon~sat)
                delay = 45
                print("Delay {} minutes due to Kiwoom server check time. Sun".format(delay))
                print("Until : {}".format(datetime.datetime.today() + datetime.timedelta(minutes=delay)))
                delay_min(delay)

            cur = db.time_series_temp.find({'type': duration})
            if cur.count() == 0:  # exception case.. retry
                continue

            status = cur.next()
            if status['last'] == (status['total']-1) and status['end_date'] == end_date:
                print("Collecting & Storing Stock {} Data is completed!".format(duration))
                break
        t_slack.notify("[Automation] Complete to collect stock data -> {}".format(duration))


if __name__ == "__main__":
    main([
        "min1",
        "min3",
        "min5",
        "min10",
        "min60",
        "day",
        "week",
        "month"
    ])
