from datetime import datetime
from datetime import timedelta
import json
import os.path
import pdb

from config import config_manager
from database.db_manager import DBM
from trading.account import Account, TradingHistory
from trading.stock import Stock
from util import constant
from util import tt_logger


class StrategyConfig(object):
    def __init__(self, strg_file):
        cfg_path = config_manager.CFG_PATH
        self.strg_file = os.path.join(cfg_path, strg_file)
        self.logger = tt_logger.TTlog().logger

        if not os.path.exists(strg_file):
            self.logger.error("{} not found..".format(strg_file))
            return None

        for k, v in json.loads(open(strg_file, encoding='utf-8').read()).items():
            setattr(self, k, v)

        self.init_index()

    def init_index(self):
        self.i_sar = 0
        self.i_saf = 0
        self.i_bar = 0
        self.i_baf = 0

    def get_sar_step(self):
        return self.sell_at_rising[self.i_sar]

    def get_saf_step(self):
        return self.sell_at_falling[self.i_saf]

    def get_bar_step(self):
        return self.buy_at_rising[self.i_bar]

    def get_baf_step(self):
        return self.buy_at_falling[self.i_baf]

    def exec_sar(self):
        self.i_sar += 1
        if self.i_sar >= len(self.sell_at_rising):
            self.init_index()

    def exec_saf(self):
        self.i_saf += 1
        if self.i_saf >= len(self.sell_at_falling):
            self.init_index()

    def exec_bar(self):
        self.i_bar += 1

    def exec_baf(self):
        self.i_baf += 1


class Strategy(object):
    """
    [Todo]
    trading_sequence에 대해서 어떻게 정의하면 좋을지 좀더 생각해봐야함
    """

    def __init__(self, strategy_cfg, condi):
        self.logger = tt_logger.TTlog().logger
        self.dbm = DBM('TopTrader')
        self.strg_name = strategy_cfg.replace(".strategy", "")
        self.strg_cfg = StrategyConfig(strategy_cfg)
        self.condi = condi
        self.condi.set_disable_code_list(self.strg_cfg.disable_code_list)
        self.th = TradingHistory(self.strg_name, self.condi.condi_index, self.condi.condi_name)
        self.acc = Account(self.strg_cfg.balance, self.th)

    def get_sell_signal_stocks(self, stock_list):
        """

        :param stock_list:
        :return:
        """
        return [stock for stock in stock_list if self.is_sell_signal(stock, self.strg_cfg)]

    def get_buy_signal_stocks(self, stock_list):
        """

        :param stock_list:
        :param strg_acc:
        :param acc:
        :return:
        """
        return [stock for stock in stock_list if self.is_buy_signal(stock)]

    def simulate(self, target_date):

        # 조건검색식으로부터 검출된 code list
        code_list = self.condi.detected_code_list(target_date)
        print(code_list)

        # 거래불가 종목을 제외
        code_list = list(set(code_list) - set(self.strg_cfg.disable_code_list))

        # stock 객체 초기화 및 time_series_sec1 생성
        for code in code_list:
            stock = Stock.get_instance(code)
            stock.gen_time_series_sec1(target_date)

        # 조건검색식으로 검출된 종목의 timeseries data 생성
        self.condi.gen_condi_history(target_date)

        # 전략파일에 명시한 거래가능시간으로 특정 일의 초단위 time series 정보를 생성
        for period in self.date_range(target_date):
            for t in period:
                # timestamp 업데이트 필요한 모든 객체에 업데이트(아마도 Account, Stock ?)
                self.update_account_n_stock(t)

                sell_flag = False

                # 보유한 주식에 대해 매도신호를 검사
                stock_list = self.acc.get_stock_list_in_account()
                for stock in self.get_sell_signal_stocks(stock_list):
                    # 주식 매도, 관련된 모든 정보 업데이트(계좌, 거래이력, 주식)
                    stock.timestamp = t
                    self.simul_sell(stock, stock.get_curr_price(t))
                    sell_flag = True

                # 이번에 매도를 했다면, 매수는 하지 않는다.
                if sell_flag:
                    continue

                # 이번 timestamp에 매도하지 않은 경우, 조건검색식으로부터 검출된 종목의 매수신호를 검사
                stock_list = self.condi.get_stock_list_at_timestamp(t)
                for stock in self.get_buy_signal_stocks(stock_list):
                    # 주식 매수, 관련된 모든 정보 업데이트(계좌, 거래이력, 주식)
                    stock.timestamp = t
                    self.simul_buy(stock, stock.get_curr_price(t))

            # 거래 period 끝난 후 일괄 청산
            self.acc.all_clear_stocks(t)

        return self

    def date_range(self, date):
        """특정일로부터 초단위 timestamp list 를 생성하여 return
        이때, *.strategy 를 참조하여, 거래가능시간을 고려한다.

        :param date: Datetime 객체
        :return:
        """
        y, m, d = date.year, date.month, date.day
        ret = []
        for s_time, e_time in self.strg_cfg.trading_time:
            h1, m1, s1 = [int(t) for t in s_time.split(":")]
            h2, m2, s2 = [int(t) for t in e_time.split(":")]
            s_date = datetime(y, m, d, h1, m1, s1)
            e_date = datetime(y, m, d, h2, m2, s2)
            datelist = [s_date + timedelta(seconds=x) for x in range(0, (e_date - s_date).seconds)]
            ret.append(datelist)
        return ret

    def update_account_n_stock(self, t):
        """timestamp가 변경된 후, 관련있는 모든 객체의 timestamp값을 업데이트 한다.
        계좌, 주식, 등등

        :param t:
        :return:
        """
        self.acc.update_account_value(t)

    def get_code_list_in_account(self):
        """현재 계좌에 보유중인 종목코드 리스트를 반환한다.

        :return:
        """
        return self.acc.get_code_list()

    def get_code_list_by_condi(self, t):
        """현재 timestamp에 검출된 종목코드 리스트를 반환한다.

        :param condi_index:
        :return:
        """
        pass

    def is_sell_signal(self, stock, strg_cfg):
        """특정 종목에 대해 현재 timestamp에 매도해야 하는지 신호를 검사한다.

        :param code:
        :return:
        """
        sar_rate, sar_amount_rate = strg_cfg.get_sar_step()
        saf_rate, saf_amount_rate = strg_cfg.get_saf_step()
        if sar_rate <= stock.수익률 or stock.수익률 <= saf_rate:
            return True

        # 종목당 최대 보유시간 만기되면 팔아야 함
        # strg_cfg.max_holding_period 값은 초단위
        holding_period = stock.get_holding_period().seconds
        if strg_cfg.max_holding_period <= holding_period:
            return True
        return False

    def sell(self, stock, strg_cfg):
        pass

    def simul_sell(self, stock, price):
        """매도를 진행하고, 매도 관련하여 모든 객체 정보를 업데이트한다.

        :param code:
        :return:
        """
        sar_rate, sar_amount_rate = self.strg_cfg.get_sar_step()
        saf_rate, saf_amount_rate = self.strg_cfg.get_saf_step()

        if sar_rate <= stock.수익률:
            reason = "SELL_AT_RISING_{}".format(self.strg_cfg.i_sar + 1)
            amount = stock.보유수량 * sar_amount_rate * 0.01
            self.strg_cfg.exec_sar()
        elif stock.수익률 <= saf_rate:
            reason = "SELL_AT_FALLING_{}".format(self.strg_cfg.i_saf + 1)
            amount = stock.보유수량 * saf_amount_rate * 0.01
            self.strg_cfg.exec_saf()
        elif self.strg_cfg.max_holding_period <= stock.get_holding_period().seconds:
            reason = "SELL_BY_EXPIRED"
            amount = stock.보유수량
            price = stock.현재가
        else:
            print("Selling with no reason...? why?? need to check")

        # Sell
        self.acc.update_sell(stock, int(price), int(amount), reason)

        # 주식을 모두다 팔면, index를 초기화 한다.
        if stock.first_trading:
            self.strg_cfg.init_index()

    def is_buy_signal(self, stock):
        """특정 종목에 대해 현재 timestamp에 매수해야 하는지 신호를 검사한다.

        :param stock:
        :return:
        """
        # 보유종목수 제한
        # 종목당 최대 매수금액 제한
        # 중복종목 매수 제한
        if (self.acc.get_stock_count() >= self.strg_cfg.max_amount_stocks) or \
            (stock.총매입금액 >= self.strg_cfg.max_buy_price_per_stock) or \
            (not stock.first_trading and not self.strg_cfg.same_stock_trading):
            return False

        # 종목당 최대 매수 금액 내에서 살수 있는 종목수가 10주가 안되면 못사는것으로..
        if not stock.first_trading:
            available = self.strg_cfg.max_buy_price_per_stock - stock.총매입금액
            amount = int(available / stock.현재가)
            if amount < 10:
                return False

        return True

    def buy(self, stock, strg_cfg):
        pass

    def simul_buy(self, stock, curr_price):
        """매수를 진행하고, 매수 관련하여 모든 객체 정보를 업데이트한다.

        :param stock:
        :return:
        """
        if stock.first_trading:
            amount = self.strg_cfg.max_buy_price_per_stock / curr_price
            self.acc.update_buy(stock, int(curr_price), int(amount), constant.FIRST_TRADING)

            return

        try:
            # 물타기/불타기 (분할매수)
            bar_rate, bar_amount_rate = self.strg_cfg.get_bar_step()  # 불타기
            baf_rate, baf_amount_rate = self.strg_cfg.get_baf_step()  # 물타기
            available = self.strg_cfg.max_buy_price_per_stock - stock.총매입금액

            if bar_rate <= stock.수익률:
                reason = "BUY_AT_RISING_{}".format(self.strg_cfg.i_bar+1)
                amount = (available * bar_amount_rate * 0.01) / stock.현재가
                self.strg_cfg.exec_bar()

            elif stock.수익률 <= baf_rate:
                reason = "BUY_AT_FALLING_{}".format(self.strg_cfg.i_baf + 1)
                amount = (available * baf_amount_rate * 0.01) / stock.현재가
                self.strg_cfg.exec_baf()

            self.acc.update_buy(stock, int(curr_price), int(amount), reason)
        except Exception:
            # except constant.BuySequenceEmptyError as e:
            msg = "매수신호 발생하였으나, 매수단계(buy_at_rising, buy_at_falling)가 정의되어 있지 않아, 추가 매수 안함"
            self.logger.error(msg)

    def plot(self):
        """시뮬레이션 결과를 plot

        :return:
        """
        pass

