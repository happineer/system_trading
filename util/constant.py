

KOSPI = "0"
KOSDAQ = "10"

FILTER_KEYWORD = ["KODEX", "TIGER", "KINDEX", "ETN", "KOSEF", "ARIRANG", "KBSTAR",
                  "선물", "TREX", "SMART", "FOCUS", "HANARO", "ATM"]

class BuySequenceEmptyError(Exception):
    """매수신호는 발생했는데, 매수 단계가 정의되어 있지 않는 경우 발생하는 예외

    """
    def __init__(self, msg):
        self.msg = "[BuySequenceEmptyError] %s" % msg

    def __str__(self):
        return self.msg