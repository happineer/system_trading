import pdb
from datetime import datetime
from datetime import timedelta
from database.db_manager import DBM
from util import common, constant
from util.tt_logger import TTlog
import pandas as pd
from config import config_manager as cfg_mgr


class Stock(object):
    """code당 1개의 객체(singleton/code)를 생성한다.

    """
    _inst = {}

    def __init__(self, code):
        self.empty = True
        self.first_trading = True  # 첫 거래인지
        self.timestamp = None
        self.first_buy_time = None

        # if add/delete index, must update self.core_index
        self.timestamp = None
        self.code = code
        self.stock_name = cfg_mgr.STOCK_INFO[code]['stock_name']
        self.현재가 = 0
        self.매매수량 = 0
        self.보유수량 = 0
        self.매매금액 = 0
        self.매입금액 = 0
        self.최대매입금액 = 0
        self.매입평균가 = 0.0
        self.평가손익 = 0.0
        self.실현손익 = 0
        self.누적손익 = 0
        self.평가금액 = 0.0
        self.수익률 = 0.0
        self.누적수익률 = 0.0
        self.평가금액변동 = 0.0
        self.매입금액변동 = 0.0
        self.실현손익변동 = 0.0
        self.core_index = ['timestamp', 'code', 'stock_name', '현재가', '매매수량', '보유수량', '매매금액', '매입금액',
                           '최대매입금액', '매입평균가', '평가손익', '실현손익', '누적손익', '평가금액', '수익률',
                           '누적수익률', '평가금액변동', '매입금액변동', '실현손익변동']
        self.check_core_index()

        self.time_series_sec1 = None
        self.logger = TTlog().logger
        self.dbm = DBM('TopTrader')

    def print_attr(self, trading_type, attr_list=None):
        if not cfg_mgr.STOCK_MONITOR:
            return
        self.logger.debug("\n" + ("-" * 100))
        self.logger.debug("[Stock] Information : {}/{}".format(self.stock_name, self.code))
        self.logger.debug("[Trading Type] -> {}-{}".format(trading_type, self.trading_reason))
        if bool(attr_list):
            attr_val = []
            for attr in attr_list:
                val = self.__getattribute__(attr)
                log_str = "{}: {}".format(attr, val)
                if isinstance(val, float):
                    log_str = "{}: {:.2f}".format(attr, val)
                attr_val.append(log_str)
            self.logger.debug("\t".join(attr_val))
        else:
            self.logger.debug(self.__repr__())
        # pass

    def __repr__(self):
        core_index = self.core_index

        # log = ["{}: {}".format(attr, str(self.__getattribute__(attr))) for attr in core_index]
        log = []
        for attr in core_index:
            val = self.__getattribute__(attr)
            log_str = "{}: {}".format(attr, val)
            if isinstance(val, float):
                log_str = "{}: {:.2f}".format(attr, val)
            log.append(log_str)
        return "\t".join(log)

    @classmethod
    def get_instance(cls, code):
        if code not in cls._inst:
            cls._inst[code] = Stock(code)
        return cls._inst[code]

    @classmethod
    def get_new_instance(cls, code, recycle_time_series=False):
        if code in cls._inst and recycle_time_series:
            time_series_sec1 = cls._inst[code].time_series_sec1
            cls._inst[code] = Stock(code)
            cls._inst[code].time_series_sec1 = time_series_sec1
        else:
            cls._inst[code] = Stock(code)
        return cls._inst[code]

    def get_holding_period(self, timestamp=None):
        """최초 해당 주식을 보유한 시간으로부터 경과된 시간을 반환한다.

        :return:
        """
        if not bool(timestamp):
            timestamp = self.timestamp

        if not bool(self.first_buy_time) or timestamp <= self.first_buy_time:
            return timedelta(seconds=0)
        return timestamp - self.first_buy_time

    def bep(self, event, price, amount=None):
        """Backup/Evaluate/PostAction

            prev : 기존 데이터
        :return:
        """
        # Backup
        self.backup()

        # dispatch Evaluate function
        eval_fn = self.__getattribute__("evaluate_{}".format(event))
        eval_fn(**{'price': price, 'amount': amount})

        # dispatch Post function
        post_fn = self.__getattribute__("post_{}".format(event))
        post_fn(**{'price': price, 'amount': amount})

        # Update

    def backup(self):
        """중요 지표들을 모두 백업한다.
        백업 지표는 앞에 '기존' 키워드가 붙는다.

        :return:
        """
        core_index = ['현재가', '매매수량', '보유수량', '매매금액', '매입금액', '최대매입금액', '매입평균가',
                      '평가손익', '실현손익', '누적손익', '평가금액', '수익률', '누적수익률']

        for index in core_index:
            val = self.__getattribute__(index)
            self.__setattr__('기존' + index, val)

    def evaluate_buy(self, **kwargs):
        price, amount = kwargs['price'], kwargs['amount']
        self.현재가 = price
        self.매매수량 = amount
        self.보유수량 = self.기존보유수량 + self.매매수량
        self.매매금액 = self.현재가 * self.매매수량
        self.매입금액 = self.기존매입금액 + self.매매금액
        self.매입금액변동 = self.매입금액 - self.기존매입금액
        self.최대매입금액 = max(self.최대매입금액, self.매입금액)
        self.매입평균가 = self.매입금액 / self.보유수량
        self.평가손익 = (self.현재가 - self.매입평균가) * self.보유수량
        # self.실현손익 = self.실현손익
        self.실현손익변동 = 0
        # self.누적손익 = self.누적손익
        self.평가금액 = self.현재가 * self.보유수량
        if self.보유수량 == 0:
            self.수익률 = 0.0
        else:
            self.수익률 = round((self.평가금액 - self.매입금액) / self.매입금액 * 100, 2)
        self.누적수익률 = round(float(self.누적손익) / self.최대매입금액 * 100, 2)
        self.평가금액변동 = self.평가금액 - self.기존평가금액

        if self.first_trading:
            self.first_buy_time = self.timestamp
        self.first_trading = False

    def post_buy(self, **kwargs):
        price, amount = kwargs['price'], kwargs['amount']
        core_index = ['timestamp', '현재가', '매입평균가', '수익률', '누적수익률', '누적손익', '매매수량', '보유수량',
                      '매입금액', '최대매입금액', '평가손익', '실현손익', '평가금액', '매매금액']
        self.print_attr('BUY', core_index)
        # pdb.set_trace()

    def evaluate_sell(self, **kwargs):
        price, amount = kwargs['price'], kwargs['amount']
        self.현재가 = price
        self.매매수량 = amount
        self.보유수량 = self.기존보유수량 - self.매매수량
        self.매매금액 = self.현재가 * self.매매수량
        self.매입금액 = self.기존매입평균가 * self.보유수량
        self.매입금액변동 = self.매입금액 - self.기존매입금액
        self.최대매입금액 = max(self.최대매입금액, self.매입금액)
        # self.매입평균가 = self.매입평균가
        self.평가손익 = (self.현재가 - self.매입평균가) * self.보유수량
        self.실현손익 = (self.현재가 - self.매입평균가) * self.매매수량
        self.실현손익변동 = self.실현손익 - self.기존실현손익
        self.누적손익 += self.실현손익
        self.평가금액 = self.현재가 * self.보유수량
        # self.기존수익률 = round((self.기존평가금액 - self.기존매입금액) / self.기존매입금액 * 100, 2)
        if self.보유수량 == 0:
            self.수익률 = 0.0
        else:
            self.수익률 = round((self.평가금액 - self.매입금액) / self.매입금액 * 100, 2)
        self.누적수익률 = round(float(self.누적손익) / self.최대매입금액 * 100, 2)
        self.평가금액변동 = self.평가금액 - self.기존평가금액

        if self.보유수량 == 0:
            self.first_trading = True
            self.first_buy_time = None

    def post_sell(self, **kwargs):
        price, amount = kwargs['price'], kwargs['amount']
        core_index = ['timestamp', '현재가', '매입평균가', '실현손익', '기존수익률', '기존누적수익률', '누적손익',
                      '매매수량', '보유수량', '매입금액', '최대매입금액', '평가손익', '평가금액', '매매금액']
        self.print_attr('SELL', core_index)
        # pdb.set_trace()

    def evaluate_change_price(self, **kwargs):
        price, amount = kwargs['price'], 0
        self.현재가 = price
        self.매매수량 = amount
        # self.보유수량 = self.기존보유수량 - self.매매수량
        self.매매금액 = 0
        # self.매입금액 = self.기존매입평균가 * self.보유수량
        # self.최대매입금액 = max(self.최대매입금액, self.매입금액)
        # self.매입평균가 = self.매입평균가
        self.평가손익 = (self.현재가 - self.매입평균가) * self.보유수량
        # self.실현손익 = (self.현재가 - self.매입평균가) * self.매매수량
        # self.누적손익 += self.실현손익
        self.평가금액 = self.현재가 * self.보유수량
        if self.보유수량 == 0:
            self.수익률 = 0.0
        else:
            self.수익률 = round((self.평가금액 - self.매입금액) / self.매입금액 * 100, 2)
        # self.누적수익률 = round(float(self.누적손익) / self.최대매입금액 * 100, 2)
        self.평가금액변동 = self.평가금액 - self.기존평가금액

    def post_change_price(self, **kwargs):
        price, amount = kwargs['price'], 0
        core_index = ['현재가', '매매수량', '보유수량', '매매금액', '매입금액', '최대매입금액', '매입평균가',
                      '평가손익', '실현손익', '누적손익', '평가금액', '수익률', '누적수익률']
        # self.print_attr('CHANGE PRICE')

    @common.type_check
    def update_sell(self, price_per_stock: int, amount: int):
        """현재가에 amount 만큼 매도를 하여, 내부 정보를 업데이트 한다.

        :param amount:
        :return:
        """
        self.bep('sell', price_per_stock, amount)

    @common.type_check
    def update_buy(self, price_per_stock: int, amount: int):
        """해당 주식을 매수하였을 경우, 관련 지표를 업데이트

        :param price_per_stock:
        :param amount:
        :return:
        """
        self.bep('buy', price_per_stock, amount)

    def update_stock_value(self, timestamp):
        """해당 주식의 현재가가 변경되었을 경우, 관련 지표를 업데이트

        :param timestamp:
        :return:
        """
        self.timestamp = timestamp
        현재가 = self.time_series_sec1.ix[timestamp]['현재가']
        self.bep('change_price', 현재가)

    def set_strategy(self, strg):
        """

        :param strg:
        :return:
        """
        self.strg = strg

    def gen_time_series_sec1(self, target_date):
        """특정종목 특정일의 초단위 tick_data(DataFrame 객체)를 생성한다.

                timestamp                현재가  volumn
                2018-08-02 09:00:00      0.0     0.0
                2018-08-02 09:00:01  15000.0   130.0
                2018-08-02 09:00:02  15000.0    91.0
                2018-08-02 09:00:03  15500.0     0.0
                ...(생략)

        :param target_date:
        :return:
        """

        if self.time_series_sec1 is not None:
            self.logger.info("{}/{} use existing gen_time_series_sec1..".format(self.stock_name, self.code))
            return self.time_series_sec1

        self.logger.info("{}/{} gen_time_series_sec1..".format(self.stock_name, self.code))
        y, m, d = target_date.year, target_date.month, target_date.day
        s_time = datetime(y, m, d, 9, 0, 0)
        e_time = datetime(y, m, d, 15, 30, 0)
        df = pd.DataFrame(self.dbm.get_tick_data(self.code, target_date, tick="1"))
        ts_group = df.groupby('timestamp')
        price = pd.DataFrame(ts_group.max()['현재가'])
        index = pd.date_range(s_time, e_time, freq='S')
        price = price.reindex(index, method='ffill', fill_value=0)
        # volumn = pd.DataFrame(ts_group.sum()['거래량'])
        # volumn = volumn.reindex(index, method='ffill', fill_value=0)
        # price['volumn'] = volumn
        # index = timestamp (freq=second)
        # 현재가 = max, ffill, fill_value=0
        # 거래량 = sum, ffill, fill_value=0
        self.time_series_sec1 = price
        return self.time_series_sec1

    def get_curr_price(self, timestamp):
        """현 시점(timestamp)의 주가를 반환한다.

        :param timestamp:
        :return:
        """
        if self.time_series_sec1 is None:
            y, m, d = timestamp.year, timestamp.month, timestamp.day
            self.time_series_sec1 = self.gen_time_series_sec1(datetime(y, m, d))

        return self.time_series_sec1.ix[timestamp]['현재가']
    
    def get_core_index(self):
        """Stock객체의 핵심 지표 리스트. 반드시 Stock객체의 속성값과 동기화가 되어야 함.
        
        :return: 
        """
        return self.core_index

    def check_core_index(self):
        """

        :return:
        """
        for index in self.get_core_index():
            self.__getattribute__(index)
