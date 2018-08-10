import pdb
from collections import defaultdict
from database.db_manager import DBM
from kiwoom.kw import Kiwoom
from trading.stock import Stock


class ConditionalSearch(object):
    _inst = {}

    def __init__(self, condi_index, condi_name):
        self.condi_index = condi_index
        self.condi_name = condi_name
        self.dbm = DBM('TopTrader')

    @classmethod
    def get_instance(cls, condi_index, condi_name):
        if condi_index not in cls._inst:
            cls._inst[condi_index] = ConditionalSearch(condi_index, condi_name)
        return cls._inst[condi_index]

    def detected_code_list(self, date):
        """특정일에 조건검색식으로부터 검출된 모든 code list 를 반환

        :param data:
        :return:
        """
        db_data = self.dbm.get_real_condi_search_data(date, self.condi_name)
        code_list = list(set([data['code'] for data in db_data]))
        return code_list

    def get_stock_list(self, date):
        """특정일에 조건검색식으로부터 검출된 모든 stock list 를 반환

        :param date:
        :return:
        """
        code_list = self.detected_code_list(date)
        stock_list = [Stock.get_instance(code) for code in code_list]
        return stock_list

    def get_stock_list_at_timestamp(self, timestamp):
        """특정시간(timestamp)에 조건검색식으로부터 검출된 stock list를 반환

        :param timestamp:
        :return:
        """
        return [Stock.get_instance(code) for code, time_series in self.condi_hist.items() if timestamp in time_series]

    def gen_condi_history(self, target_date):
        """조건검색식으로 부터 검색된 종목의 time series 정보를 생성
            {
              code1: {t1: {현재가: xx, 거래량: xx}, t1: {현재가: xx, 거래량: xx}, .., t1: {현재가: xx, 거래량: xx}},
              code2: {t1: {현재가: xx, 거래량: xx}, t1: {현재가: xx, 거래량: xx}, .., t1: {현재가: xx, 거래량: xx}}
            }
        :param target_date:
        :param condi_index:
        :return:
        """
        db_data = self.dbm.get_real_condi_search_data(target_date, self.condi_name)
        self.condi_hist = defaultdict(list)
        for data in db_data:
            code, timestamp = data['code'], data['date'].replace(microsecond=0)
            self.condi_hist[code].append(timestamp)
        return self.condi_hist
