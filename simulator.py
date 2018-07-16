
class Simulator():
    """시뮬레이터의 역할은 1종목에 대해 1개이상의 전략을 적용하여 전략을 검증해본다.
    시뮬레이터와 계좌는 1:1로 맵핑되고,

    2개이상의 전략을 검증하는 경우, 전략간에 계좌는 공유된다.
    """
    def __init__(self):
        self.account = Account()
        self.trade_cnt = {BUY: 0, SELL: 0}  # 총 거래횟수
        self.수수료 = 0
        self.s_money = 1000000
        self.e_money = 0
        self.슬리피지 = 1.5
        self.손익 = 0
        self.시간대별매매결과 = []
        self.종목별매매결과 = {}

    def init(self):
        self.account = Account()
        self.trade_cnt = {BUY: 0, SELL: 0}  # 총 거래횟수
        self.수수료 = 0
        self.s_money = 1000000
        self.e_money = 0
        self.슬리피지 = 1.5
        self.손익 = 0
        self.시간대별매매결과 = []
        self.종목별매매결과 = {}

    def set_strategy(self, strategy):
        self.strategy = strategy

    def run(self, duration, strategy=None):
        """s_date~e_date까지 1개 strategy에 대해 시뮬레이션한다.
        """
        if strategy:
            self.strategy = strategy

        time_index = self.strategy.get_time_series()
        for t in time_index:
            action, amount, price = self.strategy.decide(t)
            self.trade_cnt[action] += 1  # trade count
            self.수수료 += self.calc_수수료(price)

            if action == BUY:
                amount = self.슬리피지적용(amount, self.슬리피지)
            elif action == SELL:
                pass
            else:  # 보류
                pass

    def combination_run(self, simul_cfg):
        """run() 를 여러번 돌리고 싶은 경우 사용한다.
        """
        for duration, strategy in simul_cfg:
            strategy.set_account(self.account)
            self.run(duration, strategy)

    def conditional_run(self, duration, strategy_cfg):
        """특정기간(s_date, e_date)에 대해 전략을 돌리는데,
        순간순간 상황에 가장적합한 전략을 선택하여 매매를 수행한다.
        """
        pass

    def stats(self):
        """시뮬레이션 결과를 보여준다
        """
        pass


class Account():
    """특정 시뮬레이션에 대한 전체 계좌정보를 담는 클래스
    거래순서대로 매매기록을 저장한다.
    """
    def __int__(self):
        self.history = defaultdict(list)
        self.code_amount = 0

    def update_account(self, code, time, action, amount, price):
        if action == BUY:
            self.code_amount += amount
        elif action == SELL:
            self.code_amount -= amount

        self.history[code].append((time, action, amount, price))


sim = Simulator()
for code in stocks:
    sim.init()
    sim.run((s_date1, e_date1), Strategy1(code))
    sim.run((s_date2, e_date2), Strategy2(code))
    # sim.combination_run([(s_date1, e_date1), Strategy1(code), (s_date2, e_date2), Strategy2(code)])
    # sim.conditional_run((s_date, e_date), [(cond1, Strategy1(code)), (cond2, Strategy2(code))])
    sim.stats()



