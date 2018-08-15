import pdb
from singleton_decorator import singleton

from config import config_manager as cfg_mgr
from database.db_manager import DBM
from trading.stock import Stock
from util.tt_logger import TTlog
from util import common, constant


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
        self.총매입금액 = 0.0
        self.총최대매입금액 = 0.0
        self.총평가손익 = 0.0
        self.총손익 = 0.0  # 총평가손익 + 총누적손익
        self.추정자산 = init_balance
        self.총수익률 = 0.0
        self.총누적손익 = 0.0
        self.총누적수익률 = 0.0
        self.보유주식 = {}
        self.core_index = ['시작잔고', '예수금', '총평가금액', '총최대매입금액', '총매입금액', '총평가손익', '총손익',
                           '추정자산', '총수익률', '총누적손익', '총누적수익률']

        self.core_index = ['총누적손익', '총누적수익률', '총손익', '총수익률', '총평가손익', '총평가금액', '총매입금액',
                           '추정자산', '총최대매입금액', '예수금', '시작잔고']

        self.check_core_index()

        self.dbm = DBM('TopTrader')
        self.timestamp = None
        self.trading_history = th
        self.logger = TTlog().logger

    def print_attr(self, trading_type, stock_name, code, reason, attr_list=None):
        if not cfg_mgr.ACCOUNT_MONITOR:
            return
        self.logger.debug("\n" + ("-" * 100))
        self.logger.debug("[Account] Information : {}".format(self.timestamp))
        self.logger.debug("[Trading Type] -> {}-{} ( {}/{} )".format(trading_type, reason, stock_name, code))
        if bool(attr_list):
            attr_val = []
            for attr in attr_list:
                val = self.__getattribute__(attr)
                log_str = "{}: {}".format(attr, val)
                if isinstance(val, float):
                    log_str = "{}: {:.2f}".format(attr, val)
                attr_val.append(log_str)
            self.logger.debug("\n".join(attr_val))
        else:
            self.logger.debug(self.__repr__())

    def __repr__(self):
        core_index = ['timestamp'] + self.core_index

        # log = ["{}: {}".format(attr, str(self.__getattribute__(attr))) for attr in core_index]
        log = []
        for attr in core_index:
            val = self.__getattribute__(attr)
            log_str = "{}: {}".format(attr, val)
            if isinstance(val, float):
                log_str = "{}: {:.2f}".format(attr, val)
            log.append(log_str)
        return "\t".join(log)

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
        if cfg_mgr.debug_mode():
            pass
            # self.print_attr('SELL', stock.stock_name, stock.code, reason)
            # pdb.set_trace()

        # 계좌 정보 업데이트
        self.예수금 += stock.매매금액
        self.총평가금액 += stock.평가금액변동
        self.총매입금액 += stock.매입금액변동
        self.총최대매입금액 = max(self.총매입금액, self.총최대매입금액)
        self.추정자산 = self.예수금 + self.총평가금액  # 현금(예수금) + 주식(총평가금액)
        self.총누적손익 += stock.실현손익
        self.총평가손익 = float(self.총평가금액 - self.총매입금액)  # 보유한 주식의가치로 얻은 손익
        self.총손익 = self.총평가손익 + self.총누적손익  # 개념상 손익 (현금의 손익 + 가치의 손익)
        try:
            self.총수익률 = self.총평가손익 / self.총매입금액 * 100  # 보유한 주식에 대한 총 수익률
        except ZeroDivisionError as e:
            self.총수익률 = 0.0
        self.총누적수익률 = float(self.총누적손익) / self.총최대매입금액 * 100  # 실현한 수익에 대한 총 수익률

        self.sell_transaction(stock)

        if stock.보유수량 == 0:
            del self.보유주식[stock.code]
        else:
            self.보유주식[stock.code] = stock

        try:
            if cfg_mgr.debug_mode():
                self.print_attr('SELL', stock.stock_name, stock.code, reason)
                # pdb.set_trace()
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

        # 속성값이 겹치지 않게 잘 관리되어야 함.
        # 겹치는 속성이 있다면, Account속성에는 '총' 붙이도록 함.
        stock_index = stock.get_core_index()
        account_index = self.get_core_index()

        # temp code - allow to duplicate 'timestamp'
        ret = (set(stock_index) & set(account_index)) - set('timestamp')
        if bool(ret):
            self.logger.error("{} is duplicate index. program exit")
            exit(-1)

        tr = common.copy_attr(stock, tr, stock_index)
        tr = common.copy_attr(self, tr, account_index)

        return tr

    def sell_transaction(self, stock):
        """

        :return:
        """
        tr = self.gen_trading_info(stock, constant.SELL_TRADING_TYPE)
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

        if cfg_mgr.debug_mode():
            pass
            # self.print_attr('BUY', stock.stock_name, stock.code, reason)  # need to move to util/common pkg
            # pdb.set_trace()

        # 계좌 정보 업데이트
        self.예수금 -= stock.매매금액
        self.총평가금액 += stock.평가금액변동
        self.총매입금액 += stock.매입금액변동
        self.총최대매입금액 = max(self.총매입금액, self.총최대매입금액)
        self.추정자산 = self.예수금 + self.총평가금액  # 현금(예수금) + 주식(총평가금액)
        # self.총누적손익 += self.총누적손익 --> 변동없음
        self.총평가손익 = float(self.총평가금액 - self.총매입금액)  # 보유한 주식의가치로 얻은 손익
        self.총손익 = self.총평가손익 + self.총누적손익  # 개념상 손익 (현금의 손익 + 가치의 손익)
        self.총수익률 = self.총평가손익 / self.총매입금액 * 100  # 보유한 주식에 대한 총 수익률
        self.총누적수익률 = float(self.총누적손익) / self.총최대매입금액 * 100  # 실현한 수익에 대한 총 수익률

        # 보유주식에 포함
        self.보유주식[stock.code] = stock

        self.buy_transaction(stock)
        try:
            if cfg_mgr.debug_mode():
                self.print_attr('BUY', stock.stock_name, stock.code, reason)  # need to move to util/common pkg
                # pdb.set_trace()

        except Exception:
            # pdb.set_trace()
            print("Exception")

    def buy_transaction(self, stock):
        """

        :return:
        """
        tr = self.gen_trading_info(stock, constant.BUY_TRADING_TYPE)
        self.trading_history.record_buy_transaction(tr)

    def revaluate(self):
        """주식가치가 변경(현재가 변경)되면서 계좌에 업데이트 해야 하는 정보를 모두 업데이트

            총평가금액
            추정자산 = 예수금 + 총평가금액
            총수익률 = 총평가금액 - 총매입금액 / 총매입금액 * 100
            총손익 = (총평가금액 - 총매입금액) + 실현손익
        :return:
        """
        # self.총평가금액 = 0
        for stock in self.보유주식.values():
            # if cfg_mgr.debug_mode():
            #     self.print_attr('KEEP', stock.stock_name, stock.code, 'CHANGE_PRICE')  # need to move to util/common pkg
            #     pdb.set_trace()

            # 계좌 정보 업데이트
            # self.예수금 -= stock.매매금액
            self.총평가금액 += stock.평가금액변동
            # self.총매입금액 += stock.매입금액변동
            # self.총최대매입금액 = max(self.총매입금액, self.총최대매입금액)
            self.추정자산 = self.예수금 + self.총평가금액  # 현금(예수금) + 주식(총평가금액)
            # self.총누적손익 += self.총누적손익 --> 변동없음
            self.총평가손익 = float(self.총평가금액 - self.총매입금액)  # 보유한 주식의가치로 얻은 손익
            self.총손익 = self.총평가손익 + self.총누적손익  # 개념상 손익 (현금의 손익 + 가치의 손익)
            self.총수익률 = self.총평가손익 / self.총매입금액 * 100  # 보유한 주식에 대한 총 수익률
            # self.총누적수익률 = float(self.총누적손익) / self.총최대매입금액 * 100  # 실현한 수익에 대한 총 수익률

        # if cfg_mgr.debug_mode():
        #     self.print_attr('KEEP', stock.stock_name, stock.code, 'CHANGE_PRICE')  # need to move to util/common pkg
        #     pdb.set_trace()

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
        return [stock for stock in self.보유주식.values()]

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
        for stock in self.보유주식.values():
            self.clear_stock(stock, stock.get_curr_price(timestamp), constant.TRADING_TIME_EXPIRED)

    def get_core_index(self):
        """Account 객체의 핵심 지표 리스트. 반드시 Account 객체의 속성값과 동기화가 되어야 함.

        :return:
        """
        return self.core_index

    def check_core_index(self):
        """계좌의 핵심 지표들이 모두 설정되었는지 check.
        누락된 지표가 있다면 Exception 발생하고 프로그램 종료

        :return:
        """
        for index in self.get_core_index():
            self.__getattribute__(index)

    def is_empty(self):
        return bool(self.보유주식)


class Trading(object):
    """Trading 된 시점의 모든 데이터를 snapshot 으로 보관하는 객체
        특정시점의 모든 data를 snapshot뜨는 기능에 집중
    """
    def __init__(self, trading_type):
        self.trading_type = trading_type  # SELL, BUY (defined at constant)
        self.logger = TTlog().logger
        self.trading_core_index = [
            'timestamp', 'code', 'stock_name', 'trading_type',
            '현재가', '매매수량', '보유수량', '매매금액', '매입금액', '최대매입금액', '매입평균가',
            '평가손익', '실현손익', '누적손익', '평가금액', '수익률', '누적수익률', '평가금액변동',
            '시작잔고', '예수금', '총평가금액', '총매입금액', '총평가손익', '총손익', '추정자산',
            '총수익률', '총누적손익', '총누적수익률'
        ]

    def print_attr(self, attr_list=None):
        self.logger.debug("\n" + ("-" * 100))
        self.logger.debug("[Stock] Information : {}/{}".format(self.stock_name, self.code))
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
        core_index = self.trading_core_index
        log = []
        for attr in core_index:
            val = self.__getattribute__(attr)
            log_str = "{}: {}".format(attr, val)
            if isinstance(val, float):
                log_str = "{}: {:.2f}".format(attr, val)
            log.append(log_str)
        return "\t".join(log)

    def check_core_index(self):
        """Trading의 핵심 지표들이 모두 설정되었는지 check.
        누락된 지표가 있다면 Exception 발생하고 프로그램 종료

        :return:
        """
        for index in self.trading_core_index:
            self.__getattribute__(index)


class TradingHistory(object):
    """수많은 Trading 객체를 쉽게 조회, 가공, 분리, 재정렬 하는 기능을 제공하는 객체
        이미 생성된 여러 Trading객체를 사용자 입맛에 맞게 가공하는데 집중
        Trading관련 정보를 DB에 저장하는 임무
    """
    def __init__(self, strg_name, condi_index, condi_name):
        self.strategy_name = strg_name  # 사용한 전략명
        self.condi_name = condi_index  # buy signal을 제공한 조건검색식(buy에서만 사용)
        self.condi_index = condi_name  # buy signal을 제공한 조건검색식 index (buy에서만 사용)
        self.history = []
        self.dbm = DBM('TopTrader')
        self.logger = TTlog().logger

    def record_sell_transaction(self, trading_info):
        """

        :param trading_info:
        :return:
        """
        self.history.append(trading_info)
        # self.dbm.record_sell_transaction(trading_info)

    def record_buy_transaction(self, trading_info):
        """

        :param trading_info:
        :return:
        """
        self.history.append(trading_info)
        # self.dbm.record_buy_transaction(trading_info)

    def get_trading_history(self, **kwargs):
        """

        :return:
        """
        def search_by(trading, **kwargs):
            kwargs = {k: v for k, v in kwargs.items() if bool(v)}

            for attr, val in kwargs.items():
                if attr in ['stock_name', 'code', 'trading_type']:
                    trading_data = trading.__getattribute__(attr)
                    if trading_data != val:
                        return False
                if attr in ['period']:
                    if trading.timestamp < val[0] or val[1] < trading.timestamp:
                        return False
                if attr in ['profit_loss']:
                    if val == '+' and trading.실현손익 <= 0:
                        return False
                    if val == '-' and trading.실현손익 >= 0:
                        return False
            return True

        return [hist for hist in self.history if search_by(hist, **kwargs)]

    def view_history(self, **kwargs):
        """

        :return:
        """
        common.pprint(self.get_trading_history(**kwargs))
