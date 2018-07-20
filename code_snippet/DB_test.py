
from pymongo import MongoClient
import time
import multiprocessing


class DBM(object):
    def __init__(self):
        self.mongo = MongoClient()
        self.db = self.mongo.db_test


def fn(proc_num):
    dbm = DBM()
    data = []
    for num in range(100000):
        data.append({"proc_num": proc_num, "num": num})
        if (num % 1000) == 0:
            print("ProcNum: {}, num: {}".format(proc_num, num))
            # dbm.db.test_col.insert({"proc_num": proc_num, "num": num})
            dbm.db.test_col.insert(data)
            data = []
            time.sleep(0.1)


def main():
    proc_pool = []
    for proc_num in range(3):
        p = multiprocessing.Process(target=fn, args=(proc_num,))
        proc_pool.append(p)
        p.start()
    for p in proc_pool:
        p.join()


if __name__ == "__main__":
    main()