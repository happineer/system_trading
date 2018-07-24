
from pymongo import MongoClient
from datetime import datetime


class DBM(object):
    def __init__(self):
        self.mongo = MongoClient()
        self.db = self.mongo.TopTrader

    def get_unique_data(self, col, query=None):
        """collection의 특정 필드값을 unique 하게 얻고 싶을때 사용

            ex)
            >>> cur = self.db.trading_history.distinct("stock_name", {'date': {'$gt': datetime(2018, 7, 20, 13, 0, 0)}})

        :param col: 필드명
        :param query: 특정 조건을 만족하는 doc 를 명시하고 싶은경우 query 를 사용
        :return:
        """
        #
        if bool(query):
            cur = self.db.trading_history.distinct(col, query)
        else:
            cur = self.db.trading_history.distinct(col)
        return cur


def main():
    dbm = DBM()
    # dbm.get_unique_data("stock_name", {'date': {'$gt': datetime(2018, 7, 20, 13, 0, 0)}})


if __name__ == "__main__":
    main()