import pdb
from singleton_decorator import singleton

from config import config_manager as cfg_mgr
from database.db_manager import DBM
from trading.stock import Stock
from util.tt_logger import TTlog
from util import common


@singleton
class Account(object):
    """
    [Todo]
    구현되어야 할 api list
    -

    """
    def __init__(self, init_balance, th):
        self.시작잔고 = init_balance
        self.예수금 = init_balance
        self.총평가금액 = 0.0
        self.총매보입금액 = 0.0
        self.총손익 = 0.0
        self.추정자산 = init_balance
        self.총수익률 = 0.0
        self.실현손익 = 0.0
        self.보유주식 = {}
        self.dbm = DBM('TopTrader')
        self.timestamp = None
        self.trading_history = th
        self.logger = TTlog().logger

    def print_attr(self, trading_type):
        # self.logger.debug("\n" + ("-" * 100))
        # self.logger.debug("[Trading Type] -> {}".format(trading_type))
        # self.logger.debug(self.__repr__())
        pass

    def __repr__(self):
        core_index = ['시작잔고', '예수금', '총평가금액', '총매입금액', '총손익', '추정자산', '총수익률',
                      '실현손익', '보유주식']

        log = ["[Account] Information"]
        log += ["{}: {}".format(attr, str(self.__getattribute__(attr))) for attr in core_index]
        return "\n".join(log)

    def sync(self):
        """실제 계좌 정보를 불러와서 멤버 변수를 초기화 한다.

        :return:
        """

    @common.type_check
    def update_sell(self, stock: Stock, price_per_stock: int, amount: int, reason: str):
        """특정 주식을 매도했을때, 계좌정보를 업데이트

        :param code:
        :param amount:
        :return:
        """
        # stock 객체 업데이트
        stock.trading_reason = reason
        stock.update_sell(price_per_stock, amount)


        # 계좌 정보 업데이트
        self.예수금 += stock.총평가금액
        self.총평가금액 -= stock.총평가금액
        self.총매입금액 -= stock.총매입금액
        self.추정자산 = self.예수금 + self.총평가금액
        self.실현손익 += stock.총평가금액 - stock.총매입금액
        self.총손익 = (self.총평가금액 - self.총매입금액) + self.실현손익
        self.총수익률 = float(self.총손익) / self.시작잔고 * 100
        if stock.보유수량 == 0:
            del self.보유주식[stock.code]
        else:
            self.보유주식[stock.code] = stock

        self.sell_transaction(stock)

        try:
            self.print_attr('sell')
        except Exception:
            pdb.set_trace()
            print("Exception")
        return ""

    def gen_trading_info(self, stock, trading_type):
        """
            self.time = ""  # 또는 체결시간?
            self.trading_type = ""  # [B]uy, [S]ell
            self.code = ""  # 종목의 코드
            self.stock_name = ""  # 종목 이름
            self.stock_price = ""  # buy, sell 시 얼마에 사고팔았는지?
            self.loss_flag = None  # 손해를 봤는지, 안봤는지 (buy 일땐 None, sell 일땐 True/False
            self.profit_amount = 0  # 손해 또는 이익을 본 금액 (sell에서만 사용)
            self.profit_rate = 0.0  # 손해 또는 이익을 본 비율 (sell에서만 사용)

        :return:
        """
        tr = Trading(trading_type)

        # 속성값이 겹치는 문제....
        if trading_type == "B":  # BUY
            stock_index = ['수익률']
            account_index = ['수익률']
        else:  # SELL
            stock_index = ['수익률']
            account_index = ['수익률']

        tr = common.copy_attr(stock, tr, stock_index)
        tr = common.copy_attr(self, tr, account_index)

        return tr

    def sell_transaction(self, stock):
        """

        :return:
        """
        tr = self.gen_trading_info(stock)
        self.trading_history.record_sell_transaction(tr)

    @common.type_check
    def update_buy(self, stock: Stock, price_per_stock: int, amount: int, reason: str):
        """특정 주식을 매수했을때, 계좌정보를 업데이트

        :param code:
        :param price_per_stock:
        :param amount:
        :return:
        """
        # stock 객체 업데이트
        stock.trading_reason = reason
        stock.update_buy(price_per_stock, amount)

        # 계좌 정보 업데이트
        self.예수금 -= stock.매매금액
        self.총평가금액 += stock.총평가금액변동
        self.총매입금액 += stock.매매금액
        self.추정자산 = self.예수금 + self.총평가금액
        self.총손익 = self.총손익
        self.총수익률 = (float(self.총평가금액) - self.총매입금액) / self.총매입금액 * 100
        # self.실현손익 --> Sell 할때 업데이트 됨
        # self.총손익 --> Sell 할때 업데이트 됨
        self.보유주식[stock.code] = stock

        self.buy_transaction(stock)
        try:
            self.print_attr('buy')  # need to move to util/common pkg
        except Exception:
            pdb.set_trace()
            print("Exception")

    def buy_transaction(self, stock):
        """

        :return:
        """
        tr = self.gen_trading_info(stock)
        self.trading_history.record_buy_transaction(tr)

    def revaluate(self):
        """주식가치가 변경(현재가 변경)되면서 계좌에 업데이트 해야 하는 정보를 모두 업데이트

            총평가금액
            추정자산 = 예수금 + 총평가금액
            총수익률 = 총평가금액 - 총매입금액 / 총매입금액 * 100
            총손익 = (총평가금액 - 총매입금액) + 실현손익
        :return:
        """
        self.총평가금액 = 0
        for stock in self.보유주식.values():
            self.총평가금액 += stock.총평가금액

        self.추정자산 = self.예수금 + self.총평가금액
        self.총손익 = (self.총평가금액 - self.총매입금액) + self.실현손익
        self.총수익률 = float(self.총손익) / self.시작잔고 * 100

    def update_account_value(self, timestamp):
        """보유주식을 현 timestamp에 맞게 내부 정보를 업데이트 한다.

            변경된 현재가를 기준으로 아래 필드가 함께 업데이트 된다.
            self.수익률 = (self.현재가 - self.매입평균가) / self.매입평균가 * 100
            self.평가손익 = self.총매입금액 * self.수익률
            self.총평가금액 = self.현재가 * self.보유수량

        :param timestamp:
        :return:
        """
        self.timestamp = timestamp

        if not bool(self.보유주식):
            return

        for stock in self.보유주식.values():
            stock.update_stock_value(timestamp)

        self.revaluate()

    def add_stocks(self, code_list):
        """보유주식에 포함시킨다.

        :param code:
        :return:
        """
        for code in code_list:
            self.보유주식[code] = Stock.get_instance(code)

    def set_tick1_data(self, target_date):
        """보유한 주식(Stock)에 대해 tick1 data를 생성한다.

        :param target_date:
        :return:
        """
        for stock in self.보유주식.values():
            stock.gen_time_series_sec1(target_date)

    def get_tick_data(self, code):
        """

        :param code:
        :return:
        """
        return self.보유주식[code].tick_data

    def get_balance(self):
        """현재 잔고를 반환

        :return:
        """
        return self.balance

    def has_code(self, code):
        """해당 종목을 현재 보유중인지

        :param code:
        :return:
        """
        return code in self.보유주식

    def get_stock_count(self):
        """현재 보유중인 종목의 갯수를 반환

        :return:
        """
        return self.get_code_count()

    def get_code_count(self):
        """현재 보유중인 종목의 갯수를 반환

        :return:
        """
        return len(self.get_code_list_in_account())

    def get_code_list_in_account(self):
        """현재 보유중인 종목코드를 반환

        :return:
        """
        return self.보유주식.keys()

    def get_stock_list_in_account(self):
        """현재 보유중인 종목(Stock)을 반환

        :return:
        """
        return self.보유주식.values()

    def clear_stock(self, stock, price, reason):
        """보유한 주식중 특정 종목 일괄 청산

        :param code:
        :return:
        """
        stock.trading_reason = reason
        stock.update_sell(int(price), int(stock.보유수량))

    def all_clear_stocks(self, timestamp):
        """보유한 주식을 모두 일괄 청산

        :return:
        """
        reason = "TRADING_TIME_EXPIRED"
        for stock in self.보유주식.values():
            self.clear_stock(stock, stock.get_curr_price(timestamp), reason)


class Trading(object):
    """Trading 된 시점의 모든 데이터를 snapshot 으로 보관하는 객체
        특정시점의 모든 data를 snapshot뜨는 기능에 집중
    """
    def __init__(self, trading_type):
        self.trading_type = trading_type
        self.logger = TTlog().logger


class TradingHistory(object):
    """수많은 Trading 객체를 쉽게 조회, 가공, 분리, 재정렬 하는 기능을 제공하는 객체
        이미 생성된 여러 Trading객체를 사용자 입맛에 맞게 가공하는데 집중
        Trading관련 정보를 DB에 저장하는 임무
    """
    def __init__(self, strg_name, condi_index, condi_name):
        self.strategy_name = strg_name  # 사용한 전략명
        self.condi_name = condi_index  # buy signal을 제공한 조건검색식(buy에서만 사용)
        self.condi_index = condi_name  # buy signal을 제공한 조건검색식 index (buy에서만 사용)
        self.trading_history = []
        self.logger = TTlog().logger

    def record_sell_transaction(self, trading_info):
        """

        :param trading_info:
        :return:
        """
        self.trading_history.append(trading_info)

    def record_buy_transaction(self, trading_info):
        """

        :param trading_info:
        :return:
        """
        self.trading_history.append(trading_info)

    def get_trading_history(self):
        """

        :return:
        """
        pass
