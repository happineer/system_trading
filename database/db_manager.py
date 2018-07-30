import pymongo
from pymongo import MongoClient
from singleton_decorator import singleton
from datetime import datetime
from util.tt_logger import TTlog

@singleton
class DBM():
    def __init__(self, dbname, host=None, port=None):
        """DBM 생성자, dbname을 인자로 받는다.

        :param str db: database name
        """
        if bool(host) and bool(port):
            self.mongo = MongoClient(host=host, port=port)
        else:
            self.mongo = MongoClient()

        self.db = self.mongo.get_database(dbname)
        self.col_table = {
            "tick1": self.db.time_series_tick1,
            "tick3": self.db.time_series_tick3,
            "tick5": self.db.time_series_tick5,
            "tick10": self.db.time_series_tick10,
            "tick30": self.db.time_series_tick30,
            "min1": self.db.time_series_min1,
            "min3": self.db.time_series_min3,
            "min5": self.db.time_series_min5,
            "min10": self.db.time_series_min10,
            "min30": self.db.time_series_min30,
            "real_condi_search": self.db.real_condi_search
        }
        self.logger = TTlog(logger_name="DB").logger

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

    def get_time_series_collection(self, time_unit):
        return self.col_table[time_unit]

    def check_tick_cache(self, code, date, tick="1"):
        """특정 종목의 하루단위 tick data가 DB에 있는지 확인하고,
        DB에 있으면 cur를 반환한다.

        :param code:
        :param date:
        :param tick:
        :return:
        """
        col = self.get_time_series_collection("tick" + tick)
        date = datetime(date.year, date.month, date.day, 0, 0, 0)
        cur = col.find({'code': code, 'date': date})
        if cur.count() != 0:
            return True, cur
        return False, None

    def save_force(self, col, data, search_condition):
        try:
            col.insert(data)
        except Exception as e:
            col.update(search_condition, data, upsert=True)

    def get_tick_data(self, code, date, tick="1"):
        col = self.get_time_series_collection("tick" + tick)
        base_date = datetime(date.year, date.month, date.day)
        query = {
            'code': code,
            'date': base_date
        }
        cur = col.find(query)
        if cur.count() == 0:
            return []

        return cur.next()["time_series_1tick"]

    def save_tick_data(self, data, tick="1"):
        col = self.get_time_series_collection("tick" + tick)
        try:
            col.insert(data)
        except Exception as e:
            col.update({'date': data['date'], 'code': data['code']}, data, upsert=True)

    def get_code_list_of_rcs(self, s_date, e_date):
        cur = self.db.real_condi_search.find({'date': {'$gte': s_date, '$lte': e_date}}, {'code':1, '_id': 0})
        code_list = list({data['code'] for data in cur})
        code_list.sort()
        return code_list

    def get_code_list_condi_search_result(self, date):
        # cache
        cur = self.db.real_condi_search_cache.find({'date': date})
        if cur.count() != 0:
            self.logger.debug("hit cache (real_condi_search_cache)")
            code_list = cur.next()['code_list']
        else:
            s_date = datetime(date.year, date.month, date.day, 9, 0, 0)
            e_date = datetime(date.year, date.month, date.day, 16, 0, 0)
            code_list = self.get_code_list_of_rcs(s_date, e_date)
            self.db.real_condi_search_cache.insert({'date': date, 'code_list': code_list})
        return code_list

    def get_condi_result(self, s_date, e_date):
        query = {
            "date": {
                "$gte": s_date,
                "$lte": e_date
            },
            "event": "I"
        }
        cur = self.db.real_condi_search.find(query)

        # date, code, stock_name, condi_name
        condi_result = [data for data in cur]
        condi_result.sort(key=lambda x: x['date'])
        return condi_result

    def code_list_by_condi_id(self, condi_index, date):
        query = {
            'condi_index': condi_index,
            'date': date
        }
        cur = self.db.real_condi_search.find(query)
        code_list = [doc['code'] for doc in cur]
        return code_list

    def already_collect_tick_data(self, code, date, tick="1"):
        cur = self.db.collect_tick_data_history.find({'code': code, 'date': date, 'tick': tick})
        return cur.count() != 0

    def save_collect_tick_data_history(self, code, date, tick="1"):
        self.db.collect_tick_data_history.update({'code': code, 'date': date, 'tick': tick},
                                                 {'code': code, 'date': date, 'tick': tick},
                                                 upsert=True)

    def record_collect_tick_data_status(self, status, date, tick="1"):
        self.db.collect_tick_data_status.update(
            {"date": date, "tick": tick},
            {"status": status, "date": date, "tick": tick},
            upsert=True
        )

    def get_collect_tick_data_status(self, date, tick="1"):
        cur = self.db.collect_tick_data_status.find({'date': date, 'tick': tick})
        if cur.count() == 0:
            return "NEVER_STARTED"
        data = cur.next()
        return data['status']

    def get_real_condi_search_data(self, date, condi_name):
        y, m, d = date.year, date.month, date.day
        s_date = datetime(y, m, d, 9, 0, 0)
        e_date = datetime(y, m, d, 15, 30, 0)

        # need to fix (condi_name -> condi_index)
        # query = {'date': {'$gte': s_date, '$lte': e_date}, 'event': 'I', 'condi_index': condi_index}
        query = {'date': {'$gte': s_date, '$lte': e_date}, 'event': 'I', 'condi_name': condi_name}
        cur = self.db.real_condi_search.find(query)\
            .sort('date', pymongo.ASCENDING)
        if cur.count() == 0:
            return []
        return list(cur)
