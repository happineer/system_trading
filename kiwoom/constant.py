
class NotDefinePostFunction(KeyError):
    """
    TR의 Post Function을 정의하지 않았을 경우 발생하는 예외
    """
    def __init__(self, rqname, trcode):
        self.msg = "[Error] Post Function is not defined. (rqname=%s, trcode=%s)" % (rqname, trcode)

    def __str__(self):
        return self.msg
