
class NotDefinePostFunction(KeyError):
    """
    TR의 Post Function을 정의하지 않았을 경우 발생하는 예외
    """
    def __init__(self, rqname, trcode):
        self.msg = "[Exception-NotDefinePostFunction] Post Function is not defined. (rqname=%s, trcode=%s)" % (rqname, trcode)

    def __str__(self):
        return self.msg


class NotCorrectTypeParams(Exception):
    """
    함수 param 전달 시, type이 올바르지 않은 경우 발생하는 예외
    """
    def __init__(self, msg):
        self.msg = "[Exception-NotCorrectTypeParams] %s" % msg

    def __str__(self):
        return self.msg


stock_filter = ["KODEX", "TIGER", "KINDEX", "ETN", "KOSEF", "ARIRANG", "KBSTAR",
                "선물", "TREX", "SMART", "FOCUS", "HANARO", "ATM"]
