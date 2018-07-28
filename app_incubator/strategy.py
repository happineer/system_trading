import talib as tb
import pandas as pd


class Strategy():
    """특정 종목에 대해 매순간순간 알고리즘에 의해 매수/매도/보류결정을 한다.
    """
    def __init__(self, code, account=None):
        self.code = code
        self.job_code = self.job_category(code)
        self.account = account

    def set_account(self, account):
        self.account = account

    def get_time_series(self):
        return self.db.col.find({"code": code, s_date ~ e_date}).filter('date')

    def decide(self, t):
        self.account.update_account(code, t, action, amount, price)
        return BUY, amount



