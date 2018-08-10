import pdb
from datetime import datetime
from database.db_manager import DBM
from util import common
from util.tt_logger import TTlog
import pandas as pd
from config import config_manager as cfg_mgr


class Stock(object):
    """code당 1개의 객체(singleton/code)를 생성한다.

    """
    _inst = {}

    def __init__(self, code):
        self.code = code
        self.stock_name = cfg_mgr.STOCK_INFO[code]['stock_name']
        self.empty = True
        self.first_trading = True  # 첫 거래인지
        self.누적손익 = 0  # 트레이딩 하는 동안 손익을 누적
        self.보유수량 = 0  # 보유한 종목 수량
        self.총매입금액 = 0  # 모든 매매의 price_per_stock * amount 의 합
        self.총평가금액 = 0  # 현재가 * 보유수량
        self.매입평균가 = 0.0  # 총매입금액 / 보유수량
        self.매입금액 = 0  # 이번 거래에서 매수한 금액
        self.현재가 = 0  # 해당 주식의 현재 시장가
        self.수익률 = 0.0  # (현재가 - 매입평균가) / 매입평균가 * 100
        self.평가손익 = 0  # 총평가금액 - 총매입금액
        self.time_series_sec1 = None
        self.logger = TTlog().logger
        self.dbm = DBM('TopTrader')

    def print_attr(self, trading_type):
        self.logger.debug("\n" + ("-" * 100))
        self.logger.debug("[Trading Type] -> {}".format(trading_type))
        self.logger.debug(self.__repr__())

    def __repr__(self):
        core_index = ['누적손익', '총평가금액', '총매입금액', '평가손익', '수익률', '매입평균가', '현재가', '현재가변동',
                      '매입금액', '보유수량', '기존보유수량', '보유수량변동', '기존총평가금액', '총평가금액변동']
        log = ["[Stock] Information : {}/{}".format(self.stock_name, self.code)]
        log += ["{}: {}".format(attr, str(self.__getattribute__(attr))) for attr in core_index]
        return "\n".join(log)

    @classmethod
    def get_instance(cls, code):
        if code not in cls._inst:
            cls._inst[code] = Stock(code)
        return cls._inst[code]

    @common.type_check
    def update_sell(self, price_per_stock: int, amount: int):
        """현재가에 amount 만큼 매도를 하여, 내부 정보를 업데이트 한다.

        :param amount:
        :return:
        """

        # 기존 데이터 보관
        self.기존현재가 = self.현재가
        self.기존보유수량 = self.보유수량
        # self.기존매입금액 = self.매입금액
        self.기존총매입금액 = self.총매입금액
        self.기존매입평균가 = self.매입평균가

        # 신규 데이터 업데이트
        self.현재가 = price_per_stock
        self.보유수량 -= amount
        if self.보유수량 == 0:
            self.총매입금액 = 0
            self.매입평균가 = 0
        else:
            self.총매입금액 -= round(self.매입평균가 * amount, 0)
            self.매입평균가 = round(float(self.총매입금액) / self.보유수량, 1)

        # 지표 변경 업데이트
        self.revaluate(self.현재가, self.보유수량)
        self.누적손익 += (self.현재가 - self.기존매입평균가) * amount

        try:
            self.print_attr('sell')
        except:
            pdb.set_trace()
            print("Exception")

    @common.type_check
    def update_buy(self, price_per_stock: int, amount: int):
        """해당 주식을 매수하였을 경우, 관련 지표를 업데이트

        :param price_per_stock:
        :param amount:
        :return:
        """
        # 기존 데이터 보관
        self.기존현재가 = self.현재가
        self.기존보유수량 = self.보유수량
        # self.기존매입금액 = self.매입금액
        self.기존총매입금액 = self.총매입금액
        self.기존매입평균가 = self.매입평균가

        # 신규 데이터 업데이트
        self.현재가 = price_per_stock
        self.보유수량 += amount
        self.매입금액 = price_per_stock * amount
        self.총매입금액 += self.매입금액
        self.매입평균가 = round(float(self.총매입금액) / self.보유수량, 1)

        # 지표 변경 업데이트
        self.revaluate(price_per_stock, amount)

        try:
            self.print_attr('buy')
        except:
            pdb.set_trace()
            print("Exception")

    def update_stock_value(self, timestamp):
        현재가 = self.time_series_sec1.ix[timestamp]['현재가']
        return self.revaluate(현재가, self.보유수량)

    def revaluate(self, 신규현재가, 신규보유수량):
        """현재 "보유"한 종목의 평가 관련 지표.
            해당 주식의 현재가격이 변동될 경우, 관련지표를 업데이트 한다.
            * 주의) 현재가만 변경되는 경우 사용하는 함수(보유수량이 함께 변경되면 사용못함)

            업데이트 되는 항목
            - 현재가
            - 수익률
            - 평가손익
            - 총평가금액

        :param 현재가:
        :return:
        """
        # 기존 데이터 보관
        self.기존총평가금액 = self.총평가금액
        self.기존수익률 = self.수익률
        self.기존평가손익 = self.평가손익

        # 신규 데이터 업데이트
        self.현재가 = 신규현재가
        if self.보유수량 == 0:
            self.총평가금액 = 0.0
            self.수익률 = 0.0
            self.평가손익 = 0.0
        else:
            self.총평가금액 = 신규현재가 * 신규보유수량
            self.수익률 = round((신규현재가 - self.매입평균가) / self.매입평균가 * 100, 1)
            self.평가손익 = self.총평가금액 - self.총매입금액

        # 변경점 지표 업데이트
        self.현재가변동 = 신규현재가 - self.기존현재가
        self.보유수량변동 = 신규보유수량 - self.기존보유수량
        self.총평가금액변동 = self.총평가금액 - self.기존총평가금액
        return self

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
