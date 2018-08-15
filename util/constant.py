

KOSPI = "0"
KOSDAQ = "10"

# Trading Reason List
FIRST_TRADING = "FIRST_TRADING"
TRADING_TIME_EXPIRED = "TRADING_TIME_EXPIRED"
SHORT_TRADING_TIME_EXPIRED = "SHORT_TRADING_TIME_EXPIRED"
PRICE_RISING = "PRICE_RISING"
PRICE_FALLING = "PRICE_FALLING"


# trading_type of Trading class
SELL_TRADING_TYPE = "SELL"
BUY_TRADING_TYPE = "BUY"

# runtime mode
DEBUG = 1
RELEASE = 2

FILTER_KEYWORD = ["KODEX", "TIGER", "KINDEX", "ETN", "KOSEF", "ARIRANG", "KBSTAR",
                  "선물", "TREX", "SMART", "FOCUS", "HANARO", "ATM"]

class BuySequenceEmptyError(Exception):
    """매수신호는 발생했는데, 매수 단계가 정의되어 있지 않는 경우 발생하는 예외

    """
    def __init__(self, msg):
        self.msg = "[BuySequenceEmptyError] %s" % msg

    def __str__(self):
        return self.msg


class CopyAttributeException(Exception):
    """객체간 속성복사도중 발생한 예외

    """
    def __init__(self, msg):
        self.msg = "[CopyAttributeException] %s" % msg

    def __str__(self):
        return self.msg

