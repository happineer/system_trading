import re
from datetime import datetime


def convert_data(f, v):
    """
    open api 통신 데이터를 적절한 data type으로 변환해주는 함수
    :param f: str - field
    :param v: str - open api 의 문자열 데이터
    :return:
    """
    v = v.strip()
    if not bool(v):
        return 0

    if f in ["현재가", "거래량", "시가", "고가", "저가", "전일종가", "거래대금"]:
        if v[0] in ["+", "-"]:
            v = v[1:]
        return int(v)
    elif f in ["체결시간"]:
        regexp = "(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})"
        args = (int(n) for n in re.search(regexp, v).groups())
        return datetime(*args)
    elif f in ["일자"]:
        regexp = "(\d{4})(\d{2})(\d{2})"
        args = (int(n) for n in re.search(regexp, v).groups())
        return datetime(*args)
    elif f in ["종목코드"]:
        return v
    return v
